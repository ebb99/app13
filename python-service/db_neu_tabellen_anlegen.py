import psycopg2

# Mit der NEUEN Datenbank verbinden

# railway app11_db
# conn_url="postgresql://postgres:OJeDuueTPoUWBLvFAzAseGAjsqwrBhwg@mainline.proxy.rlwy.net:23623/railway"
# conn = psycopg2.connect(conn_url)

# railway app12_db
# conn_url="postgresql://postgres:ToiodWcahFdmxSDCdICvkUDruvJBjLQz@mainline.proxy.rlwy.net:18982/railway"
# conn = psycopg2.connect(conn_url)
 
# railway app13_db
conn_url="postgresql://postgres:YEcdMEdFRiQHkyEtsbBKsYdMnwrFqvcn@roundhouse.proxy.rlwy.net:20001/railway"
conn = psycopg2.connect(conn_url)


#localhost
# dbname = "app13_db"
# conn = psycopg2.connect(
#     host="localhost",
#     port=5432,
#     database=dbname,     
#     user="postgres",
#     password="6778"
# )

cur = conn.cursor()

# Command-Strings für die Tabellen
cmd1 = """DROP TABLE IF EXISTS users CASCADE"""
cmd2="""CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name varchar NOT NULL,
    role varchar NOT NULL,
    password varchar NOT NULL,
    CONSTRAINT users_name_unique UNIQUE (name),
    CONSTRAINT valid_role
    CHECK (role IN ('admin', 'tipper', 'familie', 'freund'))
)
"""
cmd3 = """DROP TABLE IF EXISTS gruppen"""
cmd4="""CREATE TABLE gruppen (
    id SERIAL PRIMARY KEY,
    gruppenname TEXT NOT NULL
)
"""

cmd5 = "DROP TABLE IF EXISTS vereine"
cmd6 = """CREATE TABLE vereine (
    id SERIAL PRIMARY KEY,
    vereinsname VARCHAR(255) NOT NULL,
    url TEXT)
"""

cmd7 = """DROP TABLE IF EXISTS spiele"""
cmd8 = """
CREATE TABLE spiele (
   id SERIAL PRIMARY KEY,
   heimverein TEXT NOT NULL,
   gastverein TEXT NOT NULL,
   heimtore INTEGER ,
   gasttore INTEGER ,
   anstoss TIMESTAMP NOT NULL,
   heimbild TEXT NOT NULL,
   gastbild TEXT NOT NULL,
   spielgruppe TEXT NOT NULL,
   statuswort TEXT NOT NULL
);
"""

cmd9 = """DROP TABLE IF EXISTS tips"""

cmd10 = """
CREATE TABLE tips (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spiel_id INT NOT NULL REFERENCES spiele(id) ON DELETE CASCADE,
    heimtipp INT NOT NULL,
    gasttipp INT NOT NULL,
    punkte INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_spiel UNIQUE (user_id, spiel_id)
);
"""
cmd11 = """
ALTER TABLE spiele
ALTER COLUMN anstoss TYPE timestamptz
"""

cmd12 = """DROP TABLE IF EXISTS spiele_web"""
cmd13 = """
CREATE TABLE spiele_web (
    id SERIAL PRIMARY KEY,
    spieltag VARCHAR(255) NOT NULL,
    datum VARCHAR(255) NOT NULL,
    zeit VARCHAR(255) NOT NULL,
    heimverein VARCHAR(255) NOT NULL,
    gastverein VARCHAR(255) NOT NULL, 
    score  VARCHAR(255) NOT NULL,
    kennung VARCHAR(255) NOT NULL 
);
"""

cmd14 = """DROP TABLE IF EXISTS spielplan"""
cmd15 = """
CREATE TABLE spielplan (
    id SERIAL PRIMARY KEY,
    spieltag INT NOT NULL,
    datum DATE NOT NULL,
    wochentag VARCHAR(255) NOT NULL
 );
"""



# cur.execute(cmd1) #löschen  Tabelle users, falls sie schon existiert
# cur.execute(cmd2) # users anlegen

# cur.execute(cmd3) #löschen  Tabelle gruppen, falls sie schon existiert
# cur.execute(cmd4) # gruppen anlegen

# cur.execute(cmd5) #löschen  Tabelle vereine, falls sie schon existiert
# cur.execute(cmd6) # vereine anlegen

# cur.execute(cmd7) #löschen  Tabelle spiele, falls sie schon existiert
# cur.execute(cmd8) # spiele anlegen

# cur.execute(cmd9) #
# cur.execute(cmd10)# tips anlegen

# cur.execute(cmd11) #

# cur.execute(cmd12) # löschen  Tabelle spiele_web, falls sie schon existiert
# cur.execute(cmd13) # spiele_web anlegen 

cur.execute(cmd12) # löschen  Tabelle spielplan, falls sie schon existiert
cur.execute(cmd13) # spielplan anlegen 

conn.commit()

print("✅ Aktion erfolgreich!")
cur.close()
conn.close()
