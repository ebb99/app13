from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import psycopg2

# lokal:
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="app13_db",
    user="postgres",
    password="6778"
)


# # railway app13_db
# conn_url="postgresql://postgres:YEcdMEdFRiQHkyEtsbBKsYdMnwrFqvcn@roundhouse.proxy.rlwy.net:20001/railway"
# conn = psycopg2.connect(conn_url)

cur = conn.cursor()

def datum_holen(spieltag,html):
    wochentage_de = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag", 
        "Freitag", "Samstag", "Sonntag"
    ]

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all(class_="match-date")
    print(f"Spielplan für Spieltag {spieltag} ok")
    for i, link in enumerate(links, 1):
        # print(f"{i} Spieltag: {spieltag} Datum:  {link.get_text(strip=True)}")
        datum= link.get_text(strip=True)
        spieltag_wert = int(spieltag)
        datum_wert = datetime.strptime(datum, "%d.%m.%Y").date()
        # wochentag = datum_wert.strftime("%A")
        wochentag_name = wochentage_de[datum_wert.weekday()]
        cur.execute("""
            INSERT INTO spielplan (spieltag,datum,wochentag) VALUES (%s,%s,%s)
        """, (
            spieltag_wert,
            datum_wert,
            wochentag_name
        ))
    conn.commit()


def spielplan_holen(von_spieltag, bis_spieltag):
    print(f"Spielplan holen für Spieltag {von_spieltag} bis {bis_spieltag}...")

    url_left = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/se94724/2025-2026/ro262400/spieltag/md"
    url_right = "/spiele-und-ergebnisse"
    for spieltag in range(int(von_spieltag), int(bis_spieltag) + 1):
        url = url_left + str(spieltag) + url_right
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            # print(" Lade Übersichtsseite...")
            page.goto(url)
            page.wait_for_selector("body")
            page.wait_for_timeout(1000)
            html = page.content()
            datum_holen(spieltag,html)
            browser.close()
    # print("spieleplan ok")


#  Haupt
#  Spielplan holen
cur.execute("TRUNCATE TABLE spielplan RESTART IDENTITY")
conn.commit()
spielplan_holen("1","34") # Hier könnte der HTML-Content übergeben werden, falls nötig

cur.close()
conn.close()
print("ok")




