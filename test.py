import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()

cur.executescript('DROP TABLE Artist')
cur.executescript('DROP TABLE Genre')
cur.executescript('DROP TABLE Album')
cur.executescript('DROP TABLE Track')
cur.executescript('''
CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    genre_id  INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')


fname = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None

stuff = ET.parse(fname)
for entry in stuff.findall('dict/dict/dict'):
    if ( lookup(entry, 'Track ID') is None ) : continue

    track_title = lookup(entry, 'Name')
    artist_name = lookup(entry, 'Artist')
    album_title = lookup(entry, 'Album')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time')
    genre_name = lookup(entry, 'Genre')

    if track_title is None or artist_name is None or album_title is None : 
        continue

    #print(track_title, artist_name, album_title, count, rating, length, genre_name)

    cur.execute('''INSERT OR IGNORE INTO Artist (name) 
        VALUES ( ? )''', ( artist_name, ) )
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist_name, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
        VALUES ( ?, ? )''', ( album_title, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album_title, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name) 
        VALUES ( ? )''', ( genre_name, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre_name, ))
    genre_id = cur.fetchone()[0]
    print(genre_id)

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count) 
        VALUES ( ?, ?, ?, ?, ?, ? )''', 
        ( track_title, album_id, genre_id, length, rating, count ) )


    conn.commit()
        
