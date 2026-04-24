import os
import psycopg2
import logging
import time
import re
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================
# DB VERBINDUNG
# =========================
def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL fehlt")
    return psycopg2.connect(db_url, sslmode="require")


# =========================
# SICHERES PAGE LOAD
# =========================
def safe_goto(page, url, retries=5):
    for attempt in range(retries):
        try:
            page.goto(url, timeout=15000)
            page.wait_for_load_state("domcontentloaded")
            return True

        except Exception as e:
            logging.warning(f"Fehler bei {url} (Versuch {attempt+1}): {e}")
            time.sleep(2 * (attempt + 1))

    logging.error(f"Seite endgültig fehlgeschlagen: {url}")
    return False


# =========================
# MAIN SCRAPER
# =========================
def run_scraper():
    logging.info("🚀 Scraper gestartet")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1;")
        logging.info(f"DB OK: {cur.fetchone()}")

        cur.execute("TRUNCATE TABLE spiele_web RESTART IDENTITY")
        conn.commit()

        heute = date.today()
        dat1 = heute - timedelta(days=8)
        dat2 = heute + timedelta(days=8)

        cur.execute("""
            SELECT MIN(spieltag), MAX(spieltag)
            FROM spielplan
            WHERE datum > %s AND datum < %s
        """, (dat1, dat2))

        min_tag, max_tag = cur.fetchone()

        if not min_tag or not max_tag:
            logging.warning("Keine Spieltage gefunden")
            return

        daten_holen(cur, conn, int(min_tag), int(max_tag))

    except Exception as e:
        logging.exception("SCRAPER ERROR")

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    logging.info("✅ Scraper fertig")


# =========================
# DATEN HOLEN
# =========================
def daten_holen(cur, conn, von, bis):

    base = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/se94724/2025-2026/ro262400/spieltag/md"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0"
        )

        for spieltag in range(von, bis + 1):
            url = f"{base}{spieltag}/spiele-und-ergebnisse"
            logging.info(f"🌐 Spieltag {spieltag}")

            if not safe_goto(page, url):
                continue

            html = page.content()

            game_links = extract_links(html, "liveticker")
            plan_links = extract_links(html, "info")

            logging.info(f"{len(game_links)} Spiele / {len(plan_links)} Plan")

            scrape_links(page, game_links, cur, conn, extract_game_details)
            scrape_links(page, plan_links, cur, conn, extract_game_plan_details)

        browser.close()


# =========================
# GENERISCHE SCRAPE FUNKTION
# =========================
def scrape_links(page, links, cur, conn, extractor):
    results = []

    for link in links:
        if not safe_goto(page, link):
            continue

        try:
            page.wait_for_selector("div.match-time", timeout=10000)
            data = extractor(page.content())
            results.append(data)

        except Exception as e:
            logging.warning(f"Parsing Fehler bei {link}: {e}")

    eintrag_db(cur, conn, results)


# =========================
# LINKS
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
# PARSER
# =========================
def extract_game_details(html):
    soup = BeautifulSoup(html, "html.parser")

    heim = soup.select_one("div.team-shortname-home")
    gast = soup.select_one("div.team-shortname-away")
    time_div = soup.select_one("div.match-time")
    score_div = soup.select_one("div.match-result")

    datum = extract_datum(soup)

    return {
        "spieltag_nummer": extract_spieltag(soup),
        "Datum": datum,
        "time": time_div.get_text(strip=True) if time_div else "",
        "heim": heim.get_text(strip=True) if heim else "",
        "gast": gast.get_text(strip=True) if gast else "",
        "score": score_div.get_text(strip=True) if score_div else "n/a",
        "kennung": f"{datum}_{heim.get_text(strip=True) if heim else 'n/a'}_{gast.get_text(strip=True) if gast else 'n/a'}"
    }


def extract_game_plan_details(html):
    return extract_game_details(html)


def extract_spieltag(soup):
    h = soup.find("h3", class_="hs-scoreboard-headline")
    m = re.search(r"(\d+)\.\s*Spieltag", h.text) if h else None
    return m.group(1) if m else None


def extract_datum(soup):
    h = soup.find("h3", class_="hs-scoreboard-headline")
    m = re.search(r"(\d{2}\.\d{2}\.\d{4})", h.text) if h else None
    return m.group(1) if m else None


# =========================
# DB INSERT
# =========================
def eintrag_db(cur, conn, results):

    for g in results:
        try:
            cur.execute("""
                INSERT INTO spiele_web
                (spieltag, datum, zeit, heimverein, gastverein, score, kennung)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                g["spieltag_nummer"],
                g["Datum"],
                g["time"],
                g["heim"],
                g["gast"],
                g["score"],
                g["kennung"]
            ))

        except Exception as e:
            logging.error(f"DB Fehler: {e}")
            conn.rollback()

    conn.commit()