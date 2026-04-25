import os
import psycopg2
import logging
import time
import re
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
MAX_WORKERS = 5
RETRIES = 4
DEBUG = False

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================
# DB
# =========================
def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL fehlt")
    return psycopg2.connect(db_url, sslmode="require")


# =========================
# SAFE GOTO
# =========================
def safe_goto(page, url):
    for attempt in range(RETRIES):
        try:
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            logging.warning(f"GOTO Fehler {attempt+1}: {url}")
            time.sleep(2 * (attempt + 1))
    return False


# =========================
# LINK EXTRACTOR
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
def extract_text(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else ""


def extract_spieltag(soup):
    h = soup.find("h3", class_="hs-scoreboard-headline")
    m = re.search(r"(\d+)\.\s*Spieltag", h.text) if h else None
    return m.group(1) if m else None


def extract_datum(soup):
    h = soup.find("h3", class_="hs-scoreboard-headline")
    m = re.search(r"(\d{2}\.\d{2}\.\d{4})", h.text) if h else None
    return m.group(1) if m else None


def extract_game(html):
    soup = BeautifulSoup(html, "html.parser")

    heim = extract_text(soup, "div.team-shortname-home")
    gast = extract_text(soup, "div.team-shortname-away")
    zeit = extract_text(soup, "div.match-time")
    score = extract_text(soup, "div.match-result")

    datum = extract_datum(soup)
    spieltag = extract_spieltag(soup)

    if not score:
        score = "n/a"

    return {
        "spieltag_nummer": spieltag,
        "Datum": datum,
        "time": zeit,
        "heim": heim,
        "gast": gast,
        "score": score,
        "kennung": f"{datum}_{heim}_{gast}"
    }


# =========================
# EINZELNER LINK SCRAPER
# =========================
def scrape_single(context, link):
    page = context.new_page()

    try:
        if not safe_goto(page, link):
            return None

        html = page.content()

        if "team-shortname-home" not in html:
            time.sleep(1)
            html = page.content()

        data = extract_game(html)

        if not data["heim"] or not data["gast"]:
            return None

        return data

    except Exception as e:
        logging.warning(f"Fehler bei {link}: {e}")
        return None

    finally:
        page.close()


# =========================
# PARALLELES SCRAPING
# =========================
def scrape_links_parallel(context, links):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(scrape_single, context, link) for link in links]

        for future in as_completed(futures):
            data = future.result()
            if data:
                results.append(data)

    return results


# =========================
# DB UPSERT
# =========================
def eintrag_db(cur, conn, results):

    for g in results:
        try:
            cur.execute("""
                INSERT INTO spiele_web
                (spieltag, datum, zeit, heimverein, gastverein, score, kennung)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (kennung)
                DO UPDATE SET
                    score = EXCLUDED.score,
                    zeit = EXCLUDED.zeit
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


# =========================
# MAIN LOGIK
# =========================
def run_scraper():
    logging.info("🚀 Scraper gestartet")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("TRUNCATE TABLE spiele_web RESTART IDENTITY")
        conn.commit()

        heute = date.today()
        dat1 = heute - timedelta(days=10)
        dat2 = heute + timedelta(days=10)

        cur.execute("""
            SELECT MIN(spieltag), MAX(spieltag)
            FROM spielplan
            WHERE datum > %s AND datum < %s
        """, (dat1, dat2))

        min_tag, max_tag = cur.fetchone()

        if not min_tag or not max_tag:
            logging.warning("Keine Spieltage gefunden")
            return

        base = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/se94724/2025-2026/ro262400/spieltag/md"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")

            page = context.new_page()

            for spieltag in range(int(min_tag), int(max_tag) + 1):
                url = f"{base}{spieltag}/spiele-und-ergebnisse"

                logging.info(f"🌐 Spieltag {spieltag}")

                if not safe_goto(page, url):
                    continue

                html = page.content()

                if DEBUG and spieltag == 30:
                    with open("debug30.html", "w", encoding="utf-8") as f:
                        f.write(html)

                game_links = extract_links(html, "liveticker")

                if not game_links:
                    logging.warning(f"Keine Links gefunden: {spieltag}")
                    continue

                logging.info(f"{len(game_links)} Spiele gefunden")

                results = scrape_links_parallel(context, game_links)

                if results:
                    eintrag_db(cur, conn, results)

            browser.close()

    except Exception:
        logging.exception("SCRAPER ERROR")

    finally:
        cur.close()
        conn.close()

    logging.info("✅ Scraper fertig")


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_scraper()