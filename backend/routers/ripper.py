from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import database
import time
import threading

router = APIRouter()

class LinkPayload(BaseModel):
    links: list[str]
    is_playlist: bool = False

def background_scraper(playlists, other_links):
    # This runs completely detached from the UI
    processed = list(other_links)
    if playlists:
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                page = browser.new_page()
                for p_url in playlists:
                    try:
                        page.goto(p_url, timeout=60000)
                        page.wait_for_timeout(3000)
                        # Quick logic for extracting Amazon/Spotify links would go here
                        processed.append(p_url) 
                    except Exception: pass
                browser.close()
        except Exception: pass

    with database.get_db() as conn:
        existing = set([row['link'] for row in conn.execute("SELECT link FROM queue").fetchall()])
        new_links = [l for l in processed if l not in existing]
        for link in new_links:
            conn.execute("INSERT OR IGNORE INTO queue (link, status, track_name) VALUES (?, ?, ?)", (link, "pending", "Fetching..."))

@router.post("/add")
def add_links(payload: LinkPayload, background_tasks: BackgroundTasks):
    playlists = [l for l in payload.links if 'amazon' in l.lower() or 'playlist' in l.lower()]
    direct_links = [l for l in payload.links if l not in playlists]

    if not playlists and direct_links:
        # Instant mathematical insert
        with database.get_db() as conn:
            existing = set([row['link'] for row in conn.execute("SELECT link FROM queue").fetchall()])
            new_links = [l for l in direct_links if l not in existing]
            for link in new_links:
                conn.execute("INSERT OR IGNORE INTO queue (link, status, track_name) VALUES (?, ?, ?)", (link, "pending", "Fetching..."))
        return {"message": f"Instantly queued {len(new_links)} tracks."}
    
    # Fire and forget the scraper
    background_tasks.add_task(background_scraper, playlists, direct_links)
    return {"message": "Playlists submitted. Scraping in background..."}

@router.get("/queue")
def get_queue():
    with database.get_db() as conn:
        rows = conn.execute("SELECT link, status, track_name FROM queue ORDER BY rowid DESC LIMIT 50").fetchall()
        return [dict(row) for row in rows]