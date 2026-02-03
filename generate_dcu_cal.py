import os
import requests
from icalendar import Calendar, Event
import datetime

# ดึง API Key จาก GitHub Secrets
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

# รายการแหล่งข้อมูลที่ต้องการติดตาม
UNIVERSES = [
    {"name": "DCU", "keyword_id": 312528},
    {"name": "MCU", "keyword_id": 180547}
]

# รายชื่อซีรีส์เฉพาะเรื่อง (เช่น Invincible)
SPECIFIC_TV_SHOWS = [
    {"name": "Invincible", "id": 95595}
]

def fetch_universe_data(endpoint, keyword_id):
    """ดึงข้อมูลหนังหรือซีรีส์ตาม Keyword ID"""
    url = f"https://api.themoviedb.org/3/discover/{endpoint}"
    params = {
        "api_key": TMDB_API_KEY,
        "with_keywords": keyword_id,
        "sort_by": "primary_release_date.asc" if endpoint == "movie" else "first_air_date.asc"
    }
    return requests.get(url, params=params).json().get('results', [])

def fetch_specific_tv(tv_id):
    """ดึงข้อมูลซีรีส์เฉพาะเรื่องโดยใช้ ID"""
    url = f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

def create_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Superhero Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Superhero & Invincible Calendar')

    # 1. ดึงข้อมูลจาก Universe (DCU, MCU)
    for uni in UNIVERSES:
        # ดึงหนัง
        for m in fetch_universe_data("movie", uni['keyword_id']):
            date_str = m.get('release_date')
            if date_str:
                event = Event()
                event.add('summary', f"🎥 [{uni['name']}] {m['title']}")
                event.add('dtstart', datetime.datetime.strptime(date_str, '%Y-%m-%d').date())
                cal.add_component(event)
        
        # ดึงซีรีส์ในจักรวาลนั้นๆ
        for s in fetch_universe_data("tv", uni['keyword_id']):
            date_str = s.get('first_air_date')
            if date_str:
                event = Event()
                event.add('summary', f"📺 [{uni['name']}] {s['name']}")
                event.add('dtstart', datetime.datetime.strptime(date_str, '%Y-%m-%d').date())
                cal.add_component(event)

    # 2. ดึงข้อมูลซีรีส์เฉพาะเรื่อง (Invincible)
    for show in SPECIFIC_TV_SHOWS:
        data = fetch_specific_tv(show['id'])
        # ดึงวันฉายตอนแรก (First Air Date)
        first_date = data.get('first_air_date')
        if first_date:
            event = Event()
            event.add('summary', f"🦸‍♂️ {data['name']} (Season Start)")
            event.add('dtstart', datetime.datetime.strptime(first_date, '%Y-%m-%d').date())
            cal.add_component(event)
        
        # (แถม) ดึงวันฉายตอนถัดไปถ้ามีข้อมูล (Next Episode To Air)
        next_ep = data.get('next_episode_to_air')
        if next_ep:
            event = Event()
            event.add('summary', f"🆕 {data['name']} - S{next_ep['season_number']}E{next_ep['episode_number']}")
            event.add('dtstart', datetime.datetime.strptime(next_ep['air_date'], '%Y-%m-%d').date())
            cal.add_component(event)

    # บันทึกไฟล์ (ใช้ชื่อเดิมเพื่อให้ Link เดิมยังใช้งานได้)
    with open('dcu_upcoming.ics', 'wb') as f:
        f.write(cal.to_ical())
    print("Calendar updated with DCU, MCU, and Invincible!")

if __name__ == "__main__":
    if TMDB_API_KEY:
        create_calendar()
