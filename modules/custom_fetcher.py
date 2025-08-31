# robots_fetcher.py
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse
from modules.custom_logger import CustomLogger

import requests
from urllib.robotparser import RobotFileParser

class RobotsError(Exception):
    pass

class RobotsDisallowError(RobotsError):
    def __init__(self, url: str, user_agent: str):
        super().__init__(
            f"Fetching disallowed by robots.txt for user agent "
            f"'{user_agent}': {url}."
        )
        self.url = url
        self.user_agent = user_agent

class RobotsRateLimitError(RobotsError):
    def __init__(self, url: str, wait_seconds: float):
        super().__init__(
            f"Rate-limited by robots.txt. Try again in ~{wait_seconds:.2f}s: "
            f"{url}."
        )
        self.url = url
        self.wait_seconds = wait_seconds

@dataclass
class _DomainState:
    parser: RobotFileParser
    min_delay: float  # seconds (0 if none)
    last_request_ts: Optional[float]  # monotonic timestamp

def _normalize_origin(url: str) -> Tuple[str, str, Optional[int]]:
    """
    Return a normalized origin tuple: (scheme, hostname, port or None).
    """
    parsed = urlparse(url if "://" in url else "http://" + url)
    scheme = parsed.scheme.lower() if parsed.scheme else "http"
    host = (parsed.hostname or "").lower()
    port = parsed.port
    return scheme, host, port

def _origin_to_base_url(origin: Tuple[str, str, Optional[int]]) -> str:
    scheme, host, port = origin
    netloc = host if port is None else f"{host}:{port}"
    return urlunparse((scheme, netloc, "", "", "", ""))

class CustomFetcher:
    """
    A fetcher that enforces robots.txt per origin.

    - Caches robots.txt per origin (scheme + host + port)
    - Enforces Allow/Disallow via urllib.robotparser
    - Honors Crawl-delay and Request-rate
    - Tracks last request time per origin to respect delays
    - If robots.txt can't be fetched: assumes allowed with no delay
    """

    def __init__(
        self,
        user_agent: str = "GenericBot/1.0",
        timeout: float = 10.0,
        default_min_delay: float = 0.0,
    ):
        self.logger = CustomLogger("CustomFetcher")
        self.user_agent = user_agent
        self.timeout = float(timeout)
        self.default_min_delay = max(0.0, float(default_min_delay))

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent})

        # origin -> _DomainState
        self._domains: Dict[Tuple[str, str, Optional[int]], _DomainState] = {}

    def fetch(
        self,
        url: str,
        wait: bool = True,
        method: str = "GET",
        timeout: Optional[float] = None,
        url_modifier: Optional[Callable[[str], List[str]]] = None,
        **request_kwargs,
    ) -> requests.Response:
        """
        Fetch a URL in compliance with robots.txt.

        Behavior:
        - If 'url' is disallowed, and url_modifier is provided, try each
          modified URL in order until one is allowed and (if needed) not
          rate-limited (or wait=True).
        - If all options fail, raise RobotsDisallowError or
          RobotsRateLimitError accordingly.

        Parameters:
            url: Target URL
            wait: Whether to wait for any robots delay window to pass
            method: HTTP method (default GET)
            timeout: Per-request timeout (defaults to self.timeout)
            url_modifier: A function taking the original URL and returning
                         a list of alternate URLs to try when the original
                         is disallowed.
            **request_kwargs: Forwarded to requests.Session.request

        Returns:
            requests.Response
        """
        self.logger.debug(f"Fetch requested: {url} (method={method}, wait={wait})")

        def _attempt(u: str) -> Tuple[bool, Optional[requests.Response], float, bool]:
            """
            Try to fetch a single URL.
            Returns:
                (success, response or None, remaining_delay_seconds, disallowed)
            """
            origin = self._ensure_domain_loaded(u)
            state = self._domains[origin]

            # Allow/Disallow
            if not state.parser.can_fetch(self.user_agent, u):
                self.logger.debug(f"Disallowed by robots.txt: {u}")
                return False, None, 0.0, True

            # Rate limiting
            now = time.monotonic()
            remaining = 0.0
            if state.min_delay > 0 and state.last_request_ts is not None:
                elapsed = now - state.last_request_ts
                remaining = state.min_delay - elapsed

            if remaining > 0:
                if not wait:
                    self.logger.info(
                        f"Rate-limited for {remaining:.2f}s on {u}, "
                        f"wait=False; will consider alternatives."
                    )
                    return False, None, remaining, False
                self.logger.debug(f"Sleeping {remaining:.2f}s before fetching {u}")
                time.sleep(remaining)

            # Perform request
            self.logger.info(f"Fetching {u}")
            resp = self._session.request(
                method=method,
                url=u,
                timeout=(timeout if timeout is not None else self.timeout),
                **request_kwargs,
            )

            # Update last request timestamp
            self._domains[origin].last_request_ts = time.monotonic()
            self.logger.debug(
                f"Fetched {u} with status {resp.status_code}; "
                f"min_delay={state.min_delay:.2f}s"
            )
            return True, resp, 0.0, False

        # First, try the original URL
        success, resp, remaining, disallowed = _attempt(url)
        if success:
            return resp

        # If disallowed and we have a modifier, try alternatives
        best_wait: Optional[Tuple[str, float]] = None

        if disallowed and url_modifier is not None:
            self.logger.warning(
                f"Original URL disallowed: {url}. Trying modified candidates."
            )

            # Deduplicate candidates while preserving order
            seen: set[str] = set()
            candidates: List[str] = []
            try:
                for cand in url_modifier(url) or []:
                    if cand not in seen:
                        seen.add(cand)
                        candidates.append(cand)
            except Exception as e:
                self.logger.error(
                    f"url_modifier raised an exception; skipping alternatives. {e}"
                )
                candidates = []

            for cand in candidates:
                self.logger.info(f"Trying candidate URL: {cand}")
                s, r, rem, d = _attempt(cand)
                if s: return r
                if not d and rem > 0:
                    # Candidate allowed but rate-limited and wait=False:
                    # track the shortest remaining time to inform error.
                    if best_wait is None or rem < best_wait[1]:
                        best_wait = (cand, rem)

        # No success. Decide which error to raise.
        if best_wait is not None:
            url_for_error, wait_secs = best_wait
            self.logger.error(
                f"No candidate immediately fetchable; shortest wait is "
                f"{wait_secs:.2f}s for {url_for_error}."
            )
            raise RobotsRateLimitError(url_for_error, wait_secs)

        # Either original was disallowed and no candidates helped, or
        # original was allowed but rate-limited with wait=False and no
        # modifier was provided (covered by _attempt's behavior only if we
        # were to handle original rate-limit differently). In our flow,
        # if original was allowed-but-limited and wait=False, we didn't
        # raise yet because we only branch alternatives on 'disallowed'.
        # Since we get here only when original was disallowed (disallowed=True)
        # or alternatives exhausted, raise disallow for original.
        self.logger.error(
            "All URL options disallowed by robots.txt or no alternatives provided."
        )
        raise RobotsDisallowError(url, self.user_agent)

    def get_min_delay_for(self, url: str) -> float:
        """
        Return the computed minimum delay (seconds) for the URL's origin.
        """
        origin = self._ensure_domain_loaded(url)
        delay = self._domains[origin].min_delay
        self.logger.debug(f"Min delay for origin {origin}: {delay:.2f}s")
        return delay

    def _ensure_domain_loaded(
        self, url: str
    ) -> Tuple[str, str, Optional[int]]:
        origin = _normalize_origin(url)
        if origin in self._domains:
            return origin

        base = _origin_to_base_url(origin)
        robots_url = f"{base.rstrip('/')}/robots.txt"

        parser = RobotFileParser()
        try:
            r = self._session.get(robots_url, timeout=self.timeout)
            if r.ok and r.text:
                parser.set_url(robots_url)
                parser.parse(r.text.splitlines())
                self.logger.info(
                    f"Loaded robots.txt from {robots_url} (status {r.status_code})"
                )
            else:
                parser.set_url(robots_url)
                parser.parse([])
                self.logger.warning(
                    f"No robots.txt or empty response at {robots_url}; "
                    "assuming allow with no delay."
                )
        except requests.RequestException as e:
            parser.set_url(robots_url)
            parser.parse([])
            self.logger.warning(
                f"Failed to fetch robots.txt from {robots_url}: {e}. "
                "Assuming allow with no delay."
            )

        # Compute minimum spacing from Crawl-delay and Request-rate
        cd = parser.crawl_delay(self.user_agent)
        rr = parser.request_rate(self.user_agent)

        delay_from_cd = float(cd) if cd is not None else 0.0
        delay_from_rr = 0.0
        if rr is not None and getattr(rr, "requests", None) and getattr(
            rr, "seconds", None
        ):
            if rr.requests > 0:
                delay_from_rr = float(rr.seconds) / float(rr.requests)

        min_delay = max(delay_from_cd, delay_from_rr, self.default_min_delay)

        self._domains[origin] = _DomainState(
            parser=parser,
            min_delay=min_delay,
            last_request_ts=None,
        )
        self.logger.debug(
            f"Initialized domain state for {origin}: min_delay={min_delay:.2f}s"
        )
        return origin

if __name__ == "__main__":
    fetcher = CustomFetcher(user_agent="DemoBot/1.0")

    # If the original URL is disallowed, try the homepage and /about as fallbacks
    def modifier(url: str):
        return [
            f"{url}/hehe"
        ]

    test_url = "https://example.com/some/disallowed/path"

    try:
        response = fetcher.fetch(
            test_url,
            wait=True,  # wait for crawl-delay if needed
            url_modifier=modifier,
        )
        print(f"Success: {response.url} -> {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")

    except RobotsDisallowError as e:
        print(f" Disallowed: {e}")
    except RobotsRateLimitError as e:
        print(f"Rate-limited: {e}")