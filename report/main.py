from random import randrange, choice
import string
from modules.pdf import PdfGenerator
from report.modules.generate_latex import generateLatex
from report.modules.data_classes import Place, Artist, Event

if __name__ == "__main__":
	def getRandomPlaces():
		places = []
		for _ in range(randrange(1, 200, 6)):
			name = ""
			for _ in range(randrange(5, 22)):
				name = name + choice(string.ascii_lowercase)
			places.append(Place(name))
		return places
	
	def getRandomArtists():
		artists = []
		for _ in range(randrange(1, 200, 6)):
			name = ""
			for _ in range(randrange(5, 22)):
				name = name + choice(string.ascii_lowercase)
			artists.append(Artist(name))
		return artists
	
	def getRandomEvents():
		events = []
		for _ in range(randrange(1, 200, 6)):
			name = ""
			for _ in range(randrange(5, 22)):
				name = name + choice(string.ascii_lowercase)
			events.append(Event(name))
		return events

	pdf = PdfGenerator()
	pdf.create(generateLatex(
		placeStats="a",
		eventStats="a",
		placesMultiplatform=getRandomPlaces(),
		placesTixa=getRandomPlaces(),
		placesTicketswap=getRandomPlaces(),
		placesBandsintown=getRandomPlaces(),
		placesOpenstreetmap=getRandomPlaces(),
		artistsBandsintown=getRandomArtists(),
		artistsMultiplatform=getRandomArtists(),
		artistsTicketswap=getRandomArtists(),
		eventsMultiplatform=getRandomEvents(),
		eventsTixa=getRandomEvents(),
		eventsTicketswap=getRandomEvents(),
		eventsBandsintown=getRandomEvents(),
	))