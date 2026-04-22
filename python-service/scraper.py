
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
from datetime import date, datetime, timedelta
import os
import sys
import psycopg2




def run_scraper(job_id=None, jobs=None):
    try:
        print("🚀 Scraper gestartet")

        db_url = os.environ.get("DATABASE_URL")
        print("DB URL:", db_url)

        conn = psycopg2.connect(db_url, sslmode="require")
        cur = conn.cursor()

        cur.execute("SELECT 1;")
        print("DB OK:", cur.fetchone())

        # conn.close()

    except Exception as e:
        print("❌ DB ERROR:", e)























    # # lokal:
    # conn = psycopg2.connect(
    #     host="localhost",
    #     port=5432,
    #     database="app13_db",
    #     user="postgres",
    #     password="6778"
    # )

    # cur = conn.cursor()


    def extract_game_links(html):
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        # nach diesem Muster suchen: /deutschland-bundesliga/ma######/team1_team2/liveticker
        pattern = r'/deutschland-bundesliga/ma\d+/[^/]+_[^/]+/liveticker'
        
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            
            if re.search(pattern, href):
                # URL korrekt aufbauen
                if href.startswith("//"):
                    full_url = "https:" + href
                elif href.startswith("/"):
                    full_url = "https://www.sportschau.de" + href
                else:
                    full_url = href
                    
                if full_url not in links:
                    links.append(full_url)
        
        return links[:9]

    def extract_game_plan_links(html):
        """Extrahiert LIVETICKER-Links aus Spieltag 27"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        # nach diesem Muster suchen: /deutschland-bundesliga/ma######/team1_team2/liveticker
        pattern = r'/deutschland-bundesliga/ma\d+/[^/]+_[^/]+/info'
        
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            
            if re.search(pattern, href):
                # URL korrekt aufbauen
                if href.startswith("//"):
                    full_url = "https:" + href
                elif href.startswith("/"):
                    full_url = "https://www.sportschau.de" + href
                else:
                    full_url = href
                    
                if full_url not in links:
                    links.append(full_url)
        
        return links[:9]

    def extract_game_details(html):
        """Extrahiert Teams + Score aus Liveticker"""
        soup = BeautifulSoup(html, "html.parser")

        # Score aus div.match-result auslesen
        score_div = soup.select_one("div.match-result, div.match-result-0")
        score = score_div.get_text(strip=True) if score_div else None

        # Teamnamen aus den sichtbaren Team-Klassen
        home_div = soup.select_one("div.team-shortname-home")
        away_div = soup.select_one("div.team-shortname-away")
        time_div = soup.select_one("div.match-time")
        headline_roh = soup.find("h3",class_="hs-scoreboard-headline")
        if home_div and away_div:
            heim = home_div.get_text(strip=True)
            gast = away_div.get_text(strip=True)
            time = time_div.get_text(strip=True) 
            headline= headline_roh.get_text(strip=True) 
            spieltag_match = re.search(r"(\d+)\.\s*Spieltag", headline)
            spieltag_nummer = spieltag_match.group(1) if spieltag_match else "Nicht gefunden"
            datum_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", headline  )
            datum_text = datum_match.group(1) if datum_match else "Nicht gefunden"


        else:
            # Fallback: Teamnamen aus URL-Pattern
            teams = re.findall(r'/([^/]+)_([^/]+)/liveticker', html)
            if teams:
                heim, gast = teams[0]
                heim = heim.replace("-", " ").title()
                gast = gast.replace("-", " ").title()
            else:
                heim, gast = "n/a", "n/a"

        # Score-Fallback, falls CSS-Klasse nicht vorhanden
        if not score:
            score_match = re.search(r'(\d{1,2}:\d{1,2})', html)
            score = score_match.group(1) if score_match else "n/a"

        return {"Datum": datum_text, "spieltag_nummer": spieltag_nummer, "time": time, "heim": heim, "gast": gast, "score": score}

    def extract_game_plan_details(html):
        """Extrahiert Teams + Score aus Plan"""
        soup = BeautifulSoup(html, "html.parser")

        # Score aus div.match-result auslesen
        score_div = soup.select_one("div.match-result, div.match-result-0")
        score = score_div.get_text(strip=True) if score_div else None

        # Teamnamen aus den sichtbaren Team-Klassen
        home_div = soup.select_one("div.team-shortname-home")
        away_div = soup.select_one("div.team-shortname-away")
        time_div = soup.select_one("div.match-time")
        headline_roh = soup.find("h3",class_="hs-scoreboard-headline")
        if home_div and away_div:
            heim = home_div.get_text(strip=True)
            gast = away_div.get_text(strip=True)
            time = time_div.get_text(strip=True) 
            headline= headline_roh.get_text(strip=True) 
            spieltag_match = re.search(r"(\d+)\.\s*Spieltag", headline)
            spieltag_nummer = spieltag_match.group(1) if spieltag_match else "Nicht gefunden"
            datum_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", headline  )
            datum_text = datum_match.group(1) if datum_match else "Nicht gefunden"


        else:
            # Fallback: Teamnamen aus URL-Pattern
            teams = re.findall(r'/([^/]+)_([^/]+)/liveticker', html)
            if teams:
                heim, gast = teams[0]
                heim = heim.replace("-", " ").title()
                gast = gast.replace("-", " ").title()
            else:
                heim, gast = "n/a", "n/a"

        # Score-Fallback, falls CSS-Klasse nicht vorhanden
        if not score:
            score_match = re.search(r'(\d{1,2}:\d{1,2})', html)
            score = score_match.group(1) if score_match else "n/a"

        return {"Datum": datum_text, "spieltag_nummer": spieltag_nummer, "time": time, "heim": heim, "gast": gast, "score": "n/a"}



    def eintrag_db(results):
        for game in results:
            cur.execute("""
                INSERT INTO spiele_web (spieltag, datum, zeit, heimverein, gastverein,score)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                game["spieltag_nummer"],
                game["Datum"],
                game["time"],
                game["heim"],
                game["gast"],
                game["score"]
            ))

        # Änderungen speichern und Verbindung schließen
        conn.commit()

    def daten_holen(von, bis):
        url_left = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/se94724/2025-2026/ro262400/spieltag/md"
        url_right = "/spiele-und-ergebnisse"
        von_spieltag = von
        bis_spieltag = bis
        for spieltag in range(int(von_spieltag), int(bis_spieltag) + 1):
            URL = url_left + str(spieltag) + url_right
            # print(f"URL für Spieltag {spieltag}: {URL}") 

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                # 1️ Übersichtsseite
                print(" Lade Übersichtsseite...")
                page.goto(URL)
                page.wait_for_selector("body")
                page.wait_for_timeout(2000)
                
                html = page.content()
                game_links = extract_game_links(html)
                game_plan_links = extract_game_plan_links(html)
                
                print(f" {len(game_plan_links)} PLAN-Links gefunden:")
                for i, link in enumerate(game_plan_links, 1):
                    print(f"   {i}. {link}")


                
                print(f" {len(game_links)} LIVETICKER-Links gefunden:")
                for i, link in enumerate(game_links, 1):
                    print(f"   {i}. {link}")
                
                # if not game_links:
                #     print("❌ KEINE Links gefunden! DEBUG alle hrefs:")
                #     soup = BeautifulSoup(html, "html.parser")
                #     all_hrefs = [a.get("href")[:100] for a in soup.find_all("a", href=True) if "bundesliga" in a.get("href", "").lower()]
                #     print(all_hrefs[:10])
                #     browser.close()
                #     exit()
                
                # 2️ Detailseiten
                results = []
                for i, game_url in enumerate(game_links, 1):
                    print(f"\n--- Spiel {i}/{len(game_links)} ---")
                    print(f"URL: {game_url}")
                    
                    page.goto(game_url)
                    page.wait_for_selector("body")
                    page.wait_for_timeout(4000)
                    
                    detail_html = page.content()
                    game_data = extract_game_details(detail_html)
                    game_data_plan = extract_game_plan_details(detail_html)

                    game_data["url"] = game_url
                    
                    results.append(game_data)
                    # results.append(game_data_plan)
                    # print(f"   {game_data['heim']:<20} vs {game_data['gast']:<20} : {game_data['score']}")
                    
                    time.sleep(1)
                # print(results)   
                # eintrag_excel(results)
                eintrag_db(results)     

                results = []
                for i, game_url in enumerate(game_plan_links, 1):
                    print(f"\n--- Spiel {i}/{len(game_plan_links)} ---")
                    print(f"URL: {game_url}")
                    
                    page.goto(game_url)
                    page.wait_for_selector("body")
                    page.wait_for_timeout(4000)
                    
                    detail_html = page.content()
                    game_data_plan = extract_game_plan_details(detail_html)

                    game_data_plan ["url"] = game_url
                    
                    results.append(game_data_plan)
                    # results.append(game_data_plan)
                    # print(f"   {game_data['heim']:<20} vs {game_data['gast']:<20} : {game_data['score']}")
                    
                    time.sleep(1)
                eintrag_db(results)     
                browser.close()




    #  Haupt

    # 1. spiele_web  leeren und neu füllen von bis (IDs werden zurückgesetzt)
    cur.execute("TRUNCATE TABLE spiele_web RESTART IDENTITY")
    conn.commit()
    # console.log("Tabelle spiele_web geleert. Bereite Daten vor...")
    heute = date.today()
    dat1 = heute - timedelta(days=1)
    dat2 = heute + timedelta(days=8)
    query_min_max = """
        SELECT MIN(spieltag), MAX(spieltag) 
        FROM spielplan 
        WHERE datum > %s AND datum < %s;
    """
    cur.execute(query_min_max, (dat1, dat2))
    #  Ergebnis abrufen (es ist nur eine Zeile)
    min_tag, max_tag = cur.fetchone()
    print(f"Min Spieltag: {min_tag}, Max Spieltag: {max_tag}")
    von = str(min_tag)
    bis = str(max_tag)

    daten_holen(von,bis)

    cur.close()
    conn.close()

    pass