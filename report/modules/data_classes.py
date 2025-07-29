class Place:
	def __init__(self, name, tixa_url=None, ticketswap_url=None, bandsintown_url=None, openstreetmap_id=None):
		self.name = name
		self.tixa_url = tixa_url
		self.ticketswap_url = ticketswap_url
		self.bandsintown_url = bandsintown_url
		self.openstreetmap_id = openstreetmap_id

	def __call__(self):
		return fr"""
		\subsection*{{{self.name}}}
		Hivatkozások: 
		{f"\href{{{self.tixa_url}}}{{tixa.hu}}" if self.tixa_url else ""}
		{f"\href{{{self.ticketswap_url}}}{{ticketswap.com}}" if self.ticketswap_url else ""}
		{f"\href{{{self.bandsintown_url}}}{{bandsintown.com}}" if self.bandsintown_url else ""}
		"""

class Artist:
	def __init__(self, name, ticketswap_url=None, bandsintown_url=None, openstreetmap_id=None):
		self.name = name
		self.ticketswap_url = ticketswap_url
		self.bandsintown_url = bandsintown_url
		self.openstreetmap_id = openstreetmap_id

	def __call__(self):
		return fr"""
		\subsection*{{{self.name}}}
		Hivatkozások: 
		{f"\href{{{self.ticketswap_url}}}{{ticketswap.com}}" if self.ticketswap_url else ""}
		{f"\href{{{self.bandsintown_url}}}{{bandsintown.com}}" if self.bandsintown_url else ""}
		"""

class Event:
	def __init__(self, name, tixa_url=None, ticketswap_url=None, bandsintown_url=None, openstreetmap_id=None):
		self.name = name
		self.tixa_url = tixa_url
		self.ticketswap_url = ticketswap_url
		self.bandsintown_url = bandsintown_url
		self.openstreetmap_id = openstreetmap_id

	def __call__(self):
		return fr"""
		\subsection*{{{self.name}}}
		Hivatkozások: 
		{f"\href{{{self.tixa_url}}}{{ticketswap.com}}" if self.tixa_url else ""}
		{f"\href{{{self.ticketswap_url}}}{{ticketswap.com}}" if self.ticketswap_url else ""}
		{f"\href{{{self.bandsintown_url}}}{{bandsintown.com}}" if self.bandsintown_url else ""}
		"""