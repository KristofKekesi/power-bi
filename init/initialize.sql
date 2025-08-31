CREATE TABLE IF NOT EXISTS connections (
	  artist_id int
    , event_id int
    , subevent_id int
    , place_id int
    , town_id int
		    CHECK (
            (artist_id IS NOT NULL) OR
            (event_id IS NOT NULL) OR
            (subevent_id IS NOT NULL) OR
            (place_id IS NOT NULL) OR
            (town_id IS NOT NULL)
        )
    , tixa_url varchar(2000)
       CHECK (TRIM(tixa_url) <> '')
    , ticketswap_url varchar(2000)
       CHECK (TRIM(ticketswap_url) <> '')
    , bandsintown_url varchar(2000)
       CHECK (TRIM(bandsintown_url) <> '')
    , openstreetmap_id int
        CHECK (
            (tixa_url IS NOT NULL) OR
            (ticketswap_url IS NOT NULL) OR
            (bandsintown_url IS NOT NULL) OR
            (openstreetmap_id IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS new_connections (
      tixa_url varchar(2000)
       CHECK (TRIM(tixa_url) <> '')
    , ticketswap_url varchar(2000)
       CHECK (TRIM(ticketswap_url) <> '')
    , bandsintown_url varchar(2000)
       CHECK (TRIM(bandsintown_url) <> '')
    , openstreetmap_id int
        CHECK (
            (tixa_url IS NOT NULL) OR
            (ticketswap_url IS NOT NULL) OR
            (bandsintown_url IS NOT NULL) OR
            (openstreetmap_id IS NOT NULL)
        )
    , discriminator varchar(32)
);

CREATE TABLE IF NOT EXISTS scrapes (
	  scraped_url varchar(2000)
        CHECK (TRIM(scraped_url) <> '')
    , timestamp timestamp NOT NULL
        DEFAULT current_timestamp
    , content JSONB
);