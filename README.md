# Power BI 
Ez a repó tartalmazza azokat a kódokat, amik riportokat készítenek a Tivornya tartalmával kapcsolatban.

## Megvalósítás
Konténerizált projektek, amik összehasonlítják a Tivornya tartalmait külső források tartalmaival. A készült PDF-eket AWS S3 Bucketbe tölti fel.

## Feladatok
- Tixa riport: A tixa.hu oldalon található kiemelt programok összehasonlítása a saját adatbázisban találhatóakkal. A hiányzó adatok jelentése, általános statisztika levonása csak jelen adatokra és az előző adatokhoz képest is.
- Bandsintown riport
- Funcode riport
- In-Time riport

# Fejlesztés
Futtatás
```shell
python3 -m venv .venv     # Virtuális környezet létrehozása
source .venv/bin/activate # Virtuális környezet aktiválása
python3 -m pip install -r folder/requirements.txt
PYTHONPATH=$(pwd) python3 -m folder.main
```
Merge előtt
- futtatás (lefut-e?)
```shell
python3 -m pylint --recursive=y --rcfile=folder/.pylintrc folder
```

# Teendők:
- [ ] tixa-report: Az adatbázis kapcsolat legyen opcionális.
- [ ] tixa-report: Minden ismert tixa_url megnézése hogy ott van e újdonság.