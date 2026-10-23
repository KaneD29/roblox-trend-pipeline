import os
import time
import re
import csv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pyodbc
from collections import Counter

# -------------------------------------------------------------------
# 1. Configuration & Server Setup
# -------------------------------------------------------------------
DB_CONFIG = {
    'server': r'KANE\MSSQLSERVER01',  # SSMS Server Instance
    'database': 'RobloxAnalytics',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 'cannot',
    'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll',
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while',
    'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll',
    'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves', 'https', 'com', 'www', 'discord', 'group',

    # Roblox-specific boilerplate noise
    'game', 'games', 'new', 'like', 'welcome', 'join', 'play', 'playing',
    'updates', 'update', 'favorite', 'thumbs', 'free', 'code', 'codes',
    'server', 'community', 'follow', 'check', 'out', 'every', 'get',
    'players', 'player', 'mobile', 'roblox', 'description', 'link', 'below',
    'enjoy', 'support', 'make', 'sure', 'leave', 'become', 'unlock',
    'use', 'will', 'find', 'one', 'two', 'three', 'console', 'experience',
    'team', 'world', 'buy', 'way', 'time', 'first', 'best', 'also', 'back',
    'take', 'need'
}

# Persistent HTTP Session
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})

def get_db_connection():
    conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)

def tokenize_text(text):
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS]

# -------------------------------------------------------------------
# 2. Resilient API Extraction (Flexible Top Games Fetcher)
# -------------------------------------------------------------------
def fetch_top_universe_ids(limit=1000):
    universe_ids = []

    print("Fetching Top Games across Roblox categories (Target Cap: 1000)...")
    
    # Extended list of sort categories available on Roblox discover endpoints
    sorts = [
        'top-trending', 'most-popular', 'top-rated', 
        'top-grossing', 'popular-in-country', 'top-paid'
    ]
    
    for sort_id in sorts:
        if len(universe_ids) >= limit:
            break
        url = f"https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=roblox_scraper&sortId={sort_id}&device=computer&country=all"
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                games = data.get("games", [])
                added_in_sort = 0
                for g in games:
                    u_id = g.get("universeId")
                    if u_id and u_id not in universe_ids:
                        universe_ids.append(u_id)
                        added_in_sort += 1
                print(f"Sort '{sort_id}': Added {added_in_sort} new games (Total: {len(universe_ids)})...")
        except Exception as e:
            print(f"Explore sort '{sort_id}' failed: {e}")

    # Optional Supplementing via Rolimon's Index (With strict failure exit)
    if len(universe_ids) < limit:
        print("Attempting to supplement slots via Rolimon's index...")
        rolimons_url = "https://api.rolimons.com/games/v1/gamelist"
        try:
            resp = session.get(rolimons_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                games_dict = data.get("games", {})
                
                # Sort games by active players descending
                sorted_games = sorted(games_dict.items(), key=lambda x: x[1][1] if len(x[1]) > 1 else 0, reverse=True)
                place_ids = [pid for pid, _ in sorted_games]
                
                consecutive_failures = 0
                chunk_size = 20
                
                for i in range(0, len(place_ids), chunk_size):
                    if len(universe_ids) >= limit or consecutive_failures >= 3:
                        if consecutive_failures >= 3:
                            print("Rolimon lookup stopped early due to rate limits or API cutoff.")
                        break
                        
                    chunk = place_ids[i:i + chunk_size]
                    p_ids_str = ",".join(map(str, chunk))
                    m_url = f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={p_ids_str}"
                    
                    try:
                        m_resp = session.get(m_url, timeout=5)
                        if m_resp.status_code == 200:
                            m_data = m_resp.json()
                            new_count = 0
                            for item in m_data:
                                u_id = item.get("universeId")
                                if u_id and u_id not in universe_ids:
                                    universe_ids.append(u_id)
                                    new_count += 1
                            if new_count == 0:
                                consecutive_failures += 1
                            else:
                                consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                    except Exception:
                        consecutive_failures += 1
                    
                    time.sleep(0.15)
        except Exception as e:
            print(f"Rolimon supplement failed: {e}")

    print(f"Final Collection Complete: Proceeding with {len(universe_ids)} games.")
    return universe_ids[:limit]

def fetch_game_details_batch(universe_ids_chunk):
    ids_str = ",".join(map(str, universe_ids_chunk))
    url = f"https://games.roblox.com/v1/games?universeIds={ids_str}"
    
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.json().get('data', [])
    except Exception as e:
        print(f"Error fetching game batch details: {e}")
    return []

def fetch_votes_batch(universe_ids_chunk):
    ids_str = ",".join(map(str, universe_ids_chunk))
    url = f"https://games.roblox.com/v1/games/votes?universeIds={ids_str}"
    
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            votes_data = resp.json().get('data', [])
            return {v['id']: (v['upVotes'], v['downVotes']) for v in votes_data}
    except Exception as e:
        print(f"Error fetching votes batch: {e}")
    return {}

# -------------------------------------------------------------------
# 3. ETL Execution & DB/CSV Sync
# -------------------------------------------------------------------
def run_pipeline():
    universe_ids = fetch_top_universe_ids(limit=1000)
    print(f"Processing dataset of {len(universe_ids)} collected games...")
    
    if not universe_ids:
        print("No universe IDs found. Pipeline aborting.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    global_title_words = Counter()
    global_desc_words = Counter()
    
    csv_rows = []
    
    chunk_size = 50
    for i in range(0, len(universe_ids), chunk_size):
        chunk = universe_ids[i:i + chunk_size]
        games = fetch_game_details_batch(chunk)
        votes_map = fetch_votes_batch(chunk)
        
        for g in games:
            u_id = g.get('id')
            place_id = g.get('rootPlaceId')
            name = g.get('name') or ''
            desc = g.get('description') or ''
            playing = g.get('playing', 0)
            visits = g.get('visits', 0)
            favs = g.get('favoritedCount', 0)
            
            up_votes, down_votes = votes_map.get(u_id, (0, 0))
            total_votes = up_votes + down_votes
            rating = round((up_votes / total_votes) * 100, 2) if total_votes > 0 else 0.0
            
            # Upsert into SSMS
            cursor.execute("""
                MERGE Games AS target
                USING (SELECT ? AS UniverseId) AS source
                ON (target.UniverseId = source.UniverseId)
                WHEN MATCHED THEN
                    UPDATE SET PlaceId=?, Name=?, Description=?, PlayingCount=?, Visits=?, FavoritedCount=?, UpVotes=?, DownVotes=?, RatingRatio=?, ScrapedAt=GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (UniverseId, PlaceId, Name, Description, PlayingCount, Visits, FavoritedCount, UpVotes, DownVotes, RatingRatio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, u_id, place_id, name, desc, playing, visits, favs, up_votes, down_votes, rating,
                 u_id, place_id, name, desc, playing, visits, favs, up_votes, down_votes, rating)
            
            # Text Processing
            t_words = tokenize_text(name)
            d_words = tokenize_text(desc)
            
            title_words = Counter(t_words)
            desc_words = Counter(d_words)
            
            global_title_words.update(title_words)
            global_desc_words.update(desc_words)
            
            all_game_words = set(title_words.keys()) | set(desc_words.keys())
            cursor.execute("DELETE FROM TermMatches WHERE UniverseId = ?", u_id)
            for word in all_game_words:
                cursor.execute("""
                    INSERT INTO TermMatches (UniverseId, Word, CountInTitle, CountInDescription)
                    VALUES (?, ?, ?, ?)
                """, u_id, word, title_words[word], desc_words[word])
            
            # Extract Top Terms per Game for CSV Output
            combined_counter = title_words + desc_words
            top_keywords = ", ".join([w[0] for w in combined_counter.most_common(5)])
            
            clean_desc = desc.replace("\n", " ").replace("\r", " ")
            trimmed_desc = clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc

            csv_rows.append({
                "UniverseId": u_id,
                "PlaceId": place_id,
                "Name": name,
                "PlayingCount": playing,
                "Visits": visits,
                "FavoritedCount": favs,
                "UpVotes": up_votes,
                "DownVotes": down_votes,
                "RatingRatio (%)": rating,
                "TopKeywords": top_keywords,
                "Description": trimmed_desc
            })

        conn.commit()
        print(f"Processed {min(i + chunk_size, len(universe_ids))}/{len(universe_ids)} games.")
        time.sleep(0.2)

    # Write Global Word Frequencies to Database
    print("Writing global word frequencies to database...")
    cursor.execute("TRUNCATE TABLE GlobalWordFrequency;")
    
    all_global_words = set(global_title_words.keys()) | set(global_desc_words.keys())
    for word in all_global_words:
        t_freq = global_title_words[word]
        d_freq = global_desc_words[word]
        total = t_freq + d_freq
        
        cursor.execute("""
            INSERT INTO GlobalWordFrequency (Word, TitleFrequency, DescriptionFrequency, TotalOccurrences)
            VALUES (?, ?, ?, ?)
        """, word, t_freq, d_freq, total)
        
    conn.commit()
    cursor.close()
    conn.close()

    # -------------------------------------------------------------------
    # CSV Export - Saved directly inside 'Roblox Top Game Scraper' directory
    # -------------------------------------------------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filename = os.path.join(script_dir, "roblox_top_1000_analytics.csv")
    
    print(f"Exporting dataset to '{csv_filename}'...")
    
    fieldnames = [
        "UniverseId", "PlaceId", "Name", "PlayingCount", 
        "Visits", "FavoritedCount", "UpVotes", "DownVotes", 
        "RatingRatio (%)", "TopKeywords", "Description"
    ]
    
    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Success! Exported {len(csv_rows)} rows to '{csv_filename}'.")
    print("ETL Pipeline Execution Complete.")

if __name__ == "__main__":
    run_pipeline()