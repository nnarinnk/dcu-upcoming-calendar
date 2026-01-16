import os
import requests
from icalendar import Calendar, Event
import datetime

# ดึง API Key จาก GitHub Secrets
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
DCU_KEYWORD_ID = 312528  # Keyword: DC Universe (DCU)

def fetch_tmdb_data(endpoint):
    """ฟังก์ชันช่วยดึงข้อมูลจาก TMDB ตาม endpoint ที่กำหนด"""
    url = f"https://api.themoviedb.org/3/discover/{endpoint}"
    params = {
        "api_key": TMDB_API_KEY,
        "with_keywords": DCU_KEYWORD_ID,
        "sort_by": "primary_release_date.asc" if endpoint == "movie" else "first_air_date.asc"
    }
    response = requests.get(url, params=params)
    return response.json().get('results', [])

def create_calendar():
    # 1. ดึงข้อมูลทั้งหนังและซีรีส์
    movies = fetch_tmdb_data("movie")
    tv_shows = fetch_tmdb_data("tv")
    
    cal = Calendar()
    cal.add('prodid', '-//My DCU Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'DCU Upcoming Calendar') # ตั้งชื่อปฏิทิน

    # 2. ประมวลผลข้อมูลหนัง
    for m in movies:
        release_date = m.get('release_date')
        if release_date: # ตรวจสอบว่ามีวันที่ฉายหรือไม่
            event = Event()
            event.add('summary', f"🎥 {m['title']}")
            event.add('description', f"DCU Movie\nOverview: {m.get('overview', 'No description')}")
            dt = datetime.datetime.strptime(release_date, '%Y-%m-%d').date()
            event.add('dtstart', dt)
            cal.add_component(event)

    # 3. ประมวลผลข้อมูลซีรีส์
    for s in tv_shows:
        air_date = s.get('first_air_date')
        if air_date:
            event = Event()
            event.add('summary', f"📺 {s['name']}")
            event.add('description', f"DCU Series\nOverview: {s.get('overview', 'No description')}")
            dt = datetime.datetime.strptime(air_date, '%Y-%m-%d').date()
            event.add('dtstart', dt)
            cal.add_component(event)

    # 4. บันทึกไฟล์ ics
    with open('dcu_upcoming.ics', 'wb') as f:
        f.write(cal.to_ical())
    print("Calendar updated successfully!")

if __name__ == "__main__":
    if not TMDB_API_KEY:
        print("Error: TMDB_API_KEY not found.")
    else:
        create_calendar()
