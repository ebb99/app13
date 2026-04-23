import os
import psycopg2
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
from datetime import date, timedelta


# =========================
# DB VERBINDUNG
# =========================
def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("❌ DATABASE_URL fehlt")
    return psycopg2.connect(db_url, sslmode="require")


# =========================
# MAIN SCRAPER
# =========================
def run_scraper(job_id=None, jobs=None):
    print("🚀 Scraper gestartet")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Test
        cur.execute("SELECT 1;")
        print("DB OK:", cur.fetchone())

        # Tabelle leeren
        cur.execute("TRUNCATE TABLE spiele_web RESTART IDENTITY")
        conn.commit()
        print("🧹 Tabelle geleert")

        # Zeitraum bestimmen
        heute = date.today()
        dat1 = heute - timedelta(days=1)
        dat2 = heute + timedelta(days=8)

        cur.execute("""
            SELECT MIN(spieltag), MAX(spieltag)
            FROM spielplan
            WHERE datum > %s AND datum < %s
        """, (dat1, dat2))

        min_tag, max_tag = cur.fetchone()
        print(f"📅 Spieltage: {min_tag} - {max_tag}")

        if not min_tag or not max_tag:
            print("❌ Keine Spieltage gefunden")
            return

        # Daten holen
        daten_holen(cur, conn, int(min_tag), int(max_tag))

        cur.close()
        conn.close()

        print("✅ Scraper fertig")

    except Exception as e:
        print("❌ SCRAPER ERROR:", e)


# =========================
# DATEN HOLEN
# =========================
def daten_holen(cur, conn, von, bis):
    from playwright.sync_api import sync_playwright
    base = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/se94724/2025-2026/ro262400/spieltag/md"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for spieltag in range(von, bis + 1):
            url = f"{base}{spieltag}/spiele-und-ergebnisse"
            print(f"🌐 Lade Spieltag {spieltag}")

            page.goto(url)
            page.wait_for_timeout(2000)

            html = page.content()

            game_links = extract_links(html, "liveticker")
            plan_links = extract_links(html, "info")

            print(f"🔗 {len(game_links)} Spiele, {len(plan_links)} Plan")

            # Ergebnisse
            results = []
            for link in game_links:
                page.goto(link)
                page.wait_for_timeout(3000)
                data = extract_game_details(page.content())
                results.append(data)

            eintrag_db(cur, conn, results)

            # Spielplan
            results = []
            for link in plan_links:
                page.goto(link)
                page.wait_for_timeout(3000)
                data = extract_game_plan_details(page.content())
                results.append(data)

            eintrag_db(cur, conn, results)

        browser.close()


# =========================
# LINKS EXTRAHIEREN
# =========================
def extract_links(html, typ):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    pattern = rf'/deutschland-bundesliga/ma\d+/[^/]+_[^/]+/{typ}'

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if re.search(pattern, href):
            if href.startswith("/"):
                href = "https://www.sportschau.de" + href

            if href not in links:
                links.append(href)

    return links[:9]


# =========================
# DETAILS
# =========================
def extract_game_details(html):
    soup = BeautifulSoup(html, "html.parser")

    heim = soup.select_one("div.team-shortname-home")
    gast = soup.select_one("div.team-shortname-away")
    time_div = soup.select_one("div.match-time")
    score_div = soup.select_one("div.match-result")

    return {
        "spieltag_nummer": extract_spieltag(soup),
        "Datum": extract_datum(soup),
        "time": time_div.get_text(strip=True) if time_div else "",
        "heim": heim.get_text(strip=True) if heim else "",
        "gast": gast.get_text(strip=True) if gast else "",
        "score": score_div.get_text(strip=True) if score_div else "n/a"
    }


def extract_game_plan_details(html):
    data = extract_game_details(html)
    data["score"] = "n/a"
    return data


def extract_spieltag(soup):
    h = soup.find("h3")
    if not h:
        return None
    m = re.search(r"(\d+)\.\s*Spieltag", h.text)
    return m.group(1) if m else None


def extract_datum(soup):
    h = soup.find("h3")
    if not h:
        return None
    m = re.search(r"(\d{2}\.\d{2}\.\d{4})", h.text)
    return m.group(1) if m else None


# =========================
# DB INSERT
# =========================
def eintrag_db(cur, conn, results):
    for g in results:
        cur.execute("""
            INSERT INTO spiele_web (spieltag, datum, zeit, heimverein, gastverein, score)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            g["spieltag_nummer"],
            g["Datum"],
            g["time"],
            g["heim"],
            g["gast"],
            g["score"]
        ))

    conn.commit()