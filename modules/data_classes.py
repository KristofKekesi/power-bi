from dataclasses import dataclass
from typing import Optional, List

@dataclass
class URLs:
	URL:			Optional[str] = None
	ticketURL:		Optional[str] = None
	wikipediaURL:	Optional[str] = None
	facebookURL:	Optional[str] = None
	youtubeURL:		Optional[str] = None
	instagramURL:	Optional[str] = None
	threadsURL:		Optional[str] = None
	twitterURL:		Optional[str] = None
	tiktokURL:		Optional[str] = None
	spotifyURL:		Optional[str] = None
	appleMusicURL:	Optional[str] = None
	deezerURL:		Optional[str] = None
	tixaURL:		Optional[str] = None
	ticketswapURL:	Optional[str] = None
	bandsintownURL:	Optional[str] = None

@dataclass
class ServicesAndProperties:
	accessible:					Optional[bool] = None
	buffet:						Optional[bool] = None
	isFree:						Optional[bool] = None
	freeParking:				Optional[bool] = None
	streetBikeLocker:			Optional[bool] = None
	innerBikeLocker:			Optional[bool] = None
	ownTransport:				Optional[bool] = None
	indoor:						Optional[bool] = None
	outdoor:					Optional[bool] = None
	childFriendly:				Optional[bool] = None
	animalFriendly:				Optional[bool] = None
	freeWifi:					Optional[bool] = None
	liveMusic:					Optional[bool] = None
	szepCardAcceptancePoint:	Optional[bool] = None
	hasWC:						Optional[bool] = None
	freeCloakRoom:				Optional[bool] = None
	paidCloakRoom:				Optional[bool] = None
	smokingPlace:				Optional[bool] = None

@dataclass
class Image:
	url:		str
	alt:		Optional[str] = None
	copyright:	Optional[str] = None
	license:	Optional[str] = None

@dataclass
class SEO:
	keywords:		Optional[List[str]] = None
	ageRestriction:	Optional[int] = None

@dataclass
class Artist:
	name: str
	smallDescription: Optional[str] = None
	description: Optional[str] = None
	profileImage: Optional[Image] = None
	coverImage: Optional[Image] = None
	type: str
	URLs: URLs
	seo: SEO

@dataclass
class Event:
	name: str
	smallDescription: Optional[str] = None
	description: Optional[str] = None
	coverImage: Optional[Image] = None
	capacity: Optional[int] = None
	URLs: URLs
	servicesAndProperties: ServicesAndProperties
	type: Optional[str] = None
	subType: Optional[str] = None
	placeLinks: List[str]
	placeId: Optional[int] = None
	artistLinks: List[List[str]] # Each inside list is for one artist.
	seo: SEO

@dataclass
class Place:
	name: str
	smallDescription: Optional[str] = None
	description: Optional[str] = None
	profileImage: Optional[Image] = None
	coverImage: Optional[Image] = None
	type: Optional[str] = None
	subType: Optional[str] = None
	capacity: Optional[int] = None
	URLs: URLs
	servicesAndProperties: ServicesAndProperties
	townLinks: List[str]
	townId: Optional[int] = None
	streetName: Optional[str] = None
	streetType: Optional[str] = None
	houseNumber: Optional[str] = None
	geoNumber: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	seo: SEO

@dataclass
class Subevent:
	name: str
	smallDescription: Optional[str] = None
	description: Optional[str] = None
	coverImage: Optional[Image] = None
	capacity: Optional[int] = None
	URLs: URLs
	servicesAndProperties: ServicesAndProperties
	type: Optional[str] = None
	subType: Optional[str] = None
	eventLinks: List[str]
	eventId: Optional[int] = None
	placeLinks: List[str]
	placeId: Optional[int] = None
	subPlace: Optional[str] = None
	artistLinks: List[List[str]] # Each inside list is for one artist.
	seo: SEO

if __name__ == "__main__":
	from dataclasses import asdict
	from json import dumps

	instance = URLs(URL="example.com")
	dict = asdict(instance)
	string = dumps(dict)
	print(string)