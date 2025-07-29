from os import getenv
from modules.pdf import PdfGenerator
from report.modules.data_classes import Place

pdf = PdfGenerator()

def generateLatex(
		# Stats
		placeStats=None, artistStats=None, eventStats=None,
		# Places
		placesMultiplatform=[],
		placesTixa=[],
		placesTicketswap=[],
		placesBandsintown=[],
		placesOpenstreetmap=[],
		# Artists
		artistsMultiplatform=[],
		artistsTicketswap=[],
		artistsBandsintown=[],
		# Events
		eventsMultiplatform=[],
		eventsTixa=[],
		eventsTicketswap=[],
		eventsBandsintown=[]

) -> str:
	disclaimer = getenv("DISCLAIMER")

	numberOfPlaces = len(placesMultiplatform) + len(placesTixa) + len(placesTicketswap) + len(placesBandsintown) + len(placesOpenstreetmap)
	numberOfArtists = len(artistsMultiplatform) + len(artistsTicketswap) + len(artistsBandsintown)
	numberOfEvents = len(eventsMultiplatform) + len(eventsTixa) + len(eventsTicketswap) + len(eventsBandsintown) + len(placesOpenstreetmap)
	
	numberOfItems = numberOfPlaces + numberOfArtists + numberOfEvents

	latex = fr"""
	\documentclass{{article}}

	\usepackage{{graphicx}}
	\usepackage[magyar]{{babel}}
	\usepackage{{pgfplots}}
	\usepackage{{t1enc}}
	\usepackage[hidelinks]{{hyperref}}

	\pgfplotsset{{compat=1.18}}

	\title{{Adatlefedettségi riport}}
	\author{{Forrás: power-bi}}
	\date{{Létrehozva: \today}}

	\begin{{document}}

	\maketitle
	\paragraph{{{disclaimer if disclaimer else ""}}}
	\tableofcontents

	\paragraph{{}}
	Összesen {numberOfItems} elem.

	\section{{Helyszínek ({numberOfPlaces} elem)}}
	{pdf.chart({
		"title": "Források szerint lebontva",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 6, "withConnection": 24, "missing": 14, "label": "Tixa"},
			{"withoutConnection": 4, "withConnection": 63, "missing": 13, "label": "TicketSwap"},
			{"withoutConnection": 3, "withConnection": 74, "missing": 53, "label": "Bandsintown"},
			{"withoutConnection": 102, "withConnection": 0, "missing": 120, "label": "OpenStreetMap"}
		]
	}) if placeStats else ""}
	{pdf.chart({
		"title": "Összesített",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 6, "withConnection": 24, "missing": 14, "label": ""}
		]
	}) if placeStats else ""}

	\subsection{{Multiplatform ({len(placesMultiplatform)} elem)}}
	{" ".join(map(lambda place: place.__call__(), placesMultiplatform))}

	\subsection{{Tixa ({len(placesTixa)} elem)}}
	Olyan helyszínek, amik csak a Tixa platformon találhatóak.
	{" ".join(map(lambda place: place.__call__(), placesTixa))}

	\subsection{{TicketSwap ({len(placesTicketswap)} elem)}}
	Olyan helyszínek, amik csak a TicketSwap platformon találhatóak.
	{" ".join(map(lambda place: place.__call__(), placesTicketswap))}
	
	\subsection{{Bandsintown ({len(placesBandsintown)} elem)}}
	Olyan helyszínek, amik csak a Bandsintown platformon találhatóak.
	{" ".join(map(lambda place: place.__call__(), placesBandsintown))}

	\subsection{{OpenStreetMap ({len(placesOpenstreetmap)} elem)}}
	Olyan helyszínek, amik csak az OpenStreetMap térképen találhatóak.
	{" ".join(map(lambda place: place.__call__(), placesOpenstreetmap))}

	\section{{Előadók ({numberOfArtists} elem)}}
	{pdf.chart({
		"title": "Források szerint lebontva",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 4, "withConnection": 63, "missing": 13, "label": "TicketSwap"},
			{"withoutConnection": 3, "withConnection": 74, "missing": 53, "label": "Bandsintown"}
		]
	}) if artistStats else ""}
	{pdf.chart({
		"title": "Összesített",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 6, "withConnection": 24, "missing": 14, "label": ""}
		]
	}) if artistStats else ""}

	\subsection{{Multiplatform ({len(artistsMultiplatform)} elem)}}
	{" ".join(map(lambda artist: artist.__call__(), artistsMultiplatform))}

	\subsection{{TicketSwap ({len(artistsTicketswap)} elem)}}
	Olyan előadók, amik csak a Tixa platformon találhatóak.
	{" ".join(map(lambda artist: artist.__call__(), artistsTicketswap))}

	\subsection{{Bandsintown ({len(artistsBandsintown)} elem)}}
	Olyan előadók, amik csak a Bandsintown platformon találhatóak.
	{" ".join(map(lambda artist: artist.__call__(), artistsBandsintown))}

	\section{{Programok ({numberOfEvents} elem)}}
	{pdf.chart({
		"title": "Források szerint lebontva",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 6, "withConnection": 24, "missing": 14, "label": "Tixa"},
			{"withoutConnection": 4, "withConnection": 63, "missing": 13, "label": "TicketSwap"},
			{"withoutConnection": 3, "withConnection": 74, "missing": 53, "label": "Bandsintown"}
		]
	}) if eventStats else ""}
	{pdf.chart({
		"title": "Összesített",
		"ylabel": "Elemszám",
		"formatting": {
			"withoutConnection": {"fill": "orange!70",  "legend": "Adatbáziban (összeköttetés nélkül)"},
			"withConnection": {"fill": "green!70", "legend": "Adatbáziban (összeköttetéssel)"},
			"missing": {"fill": "red!70", "legend": "Hiányzók"},
		},
		"values": [
			{"withoutConnection": 6, "withConnection": 24, "missing": 14, "label": ""}
		]
	}) if eventStats else ""}

	\subsection{{Multiplatform ({len(eventsMultiplatform)} elem)}}
	{" ".join(map(lambda event: event.__call__(), eventsMultiplatform))}

	\subsection{{Tixa ({len(eventsTixa)} elem)}}
	Olyan programok, amik csak a Tixa platformon találhatóak.
	{" ".join(map(lambda event: event.__call__(), eventsTixa))}

	\subsection{{TicketSwap ({len(eventsTicketswap)} elem)}}
	Olyan programok, amik csak a TicketSwap platformon találhatóak.
	{" ".join(map(lambda event: event.__call__(), eventsTicketswap))}

	\subsection{{Bandsintown ({len(eventsBandsintown)} elem)}}
	Olyan programok, amik csak a Bandsintown platformon találhatóak.
	{" ".join(map(lambda event: event.__call__(), eventsBandsintown))}

	\end{{document}}
	"""

	print(latex)
	return latex