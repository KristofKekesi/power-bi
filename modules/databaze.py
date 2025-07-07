from modules.db import connect_to_db
from modules.playwright_kod_copy import scrape
import re
from modules.pdf import Data,PDFData
from datetime import date
from unidecode import unidecode

cur = connect_to_db("DATA").cursor()
lista = scrape()
for i in range(len(lista)):
    for k in range(len(lista[i])):
        lista[i][k] = unidecode(lista[i][k])

def remove(text):
    pattern = r'\s(@|//).*'
    return re.sub(pattern, '', text).rstrip()

def helyek():
    db = set()
    adatok_noism = []
    akt = 0
    for i in range(len(lista)):
            hely,hlink,nev,nlink,datum = lista[i]
            db.add(hely)
            if akt != len(db):
                adatok_noism.append([hely,hlink])
                akt = len(db)
    return adatok_noism

def event_in_database():
    vegeredméy = []
    for i in range(len(helyek())):
        hely,hl = helyek()[i]
        akthely = f"'{hl}');"
        mainsq = "SELECT name, url.tixa_url FROM events event JOIN urls url ON url.event_id = event.id WHERE event.place_id IN (SELECT id FROM places place JOIN urls url ON url.place_id = place.id WHERE url.tixa_url = "
        summa = mainsq+akthely
        cur.execute(summa)
        sor = cur.fetchall()
        if len(sor) != 0:
            for i in range(len(sor)):
                vegeredméy.append([remove(sor[i][0].strip()),sor[i][1].strip(),hl])

    pdfdata = []
    for i in range(len(vegeredméy)):
        for j in range(len(lista)):
            nev,nevlink,hl = vegeredméy[i]
            hely,helink,ne,nelink,datum = lista[j]
            ne = remove(ne)
            if nev == ne and nevlink == nelink and hl == helink:
                pdfdata.append(Data(ne,"Az esemény már szerepel az adatbázisban.","https://www.tivornya.hu","success"))
                lista.remove(lista[j])
                break
    
    for k in range(len(lista)):
        hely,helink,ne,nelink,datum = lista[k]
        pdfdata.append(Data(ne,"Az esemény nem szerepel az adatbázisban.","https://www.tivornya.hu","fail"))

    return pdfdata

def place_and_url():
    cur.execute("SELECT place.name,url.tixa_url FROM places place JOIN urls url ON place.id = url.place_id")
    sor = cur.fetchall()
    pdfveg = []
    places_scrape = helyek()
    delete_places_scrape = places_scrape.copy()
    for k in range(len(places_scrape)):
        for i in range(len(sor)):
            ne,nelink = sor[i]
            ne = unidecode(ne.strip())
            if nelink != None:
                nelink = nelink.strip()
            if places_scrape[k][0] == ne:
                if places_scrape[k][1] == nelink:                
                    pdfveg.append(Data(places_scrape[k][0],"A név és link benne van az adatbázisban","https://www.tivornya.hu","success"))
                    delete_places_scrape.remove(places_scrape[k])
                    break
                if places_scrape[k][0] == None:
                    pdfveg.append(Data(places_scrape[k][0],"A név benne van adatbázisban","https://www.tivornya.hu","normal"))
                    delete_places_scrape.remove(places_scrape[k])
                    break
    for h,hl in delete_places_scrape:
        pdfveg.append(Data(h,"A név és a linnk nincs benne van adatbázisban","https://www.tivornya.hu","fail"))
    return pdfveg

def place_not_in_databese():
    cur.execute("SELECT place.name FROM places place")
    sor = cur.fetchall()
    pdfveg = []
    places_scrape = helyek()
    delete_places_scrape = places_scrape.copy()
    for i in range(len(places_scrape)):
        for k in range(len(sor)):
            if places_scrape[i][0] == sor[k][0]:
                pdfveg.append(Data(places_scrape[i][0],"A hely benne van az adatbázisban","https://www.tivornya.hu","success"))
                delete_places_scrape.remove(places_scrape[i])
                break

    for h,hl in delete_places_scrape:
        pdfveg.append(Data(h,"A hely nincs benne  az adatbázisban","https://www.tivornya.hu","fail"))

    return pdfveg

def report_make():
    all_querys = event_in_database() + place_and_url() + place_not_in_databese ()
    pdf = PDFData("Teszt riport", date.today())
    pdf.set(all_querys)
    pdf.create()
