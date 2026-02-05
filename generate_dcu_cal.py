import os
import requests
from icalendar import Calendar, Event
import datetime

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
# กำหนดให้ดูข้อมูลตั้งแต่วันที่ 1 ของเดือนที่แล้ว เพื่อไม่ให้พลาดเรื่องที่เพิ่งฉาย
START_LOOKBACK = (datetime.date.today() - datetime.timedelta(days=45)).isoformat()

# รายชื่อซีรีส์ที่ต้องการติดตามแบบเจาะจง (เพื่อให้ดึง Season ใหม่ๆ ได้แม่นยำ)
WATCH_LIST_TV = [
    {"name": "Invincible", "id": 95595},
    {"name": "Daredevil: Born Again", "id": 114472},
    {"name": "Wonder Man", "id": 204543},
    {"name": "The Boys", "id": 76479}
]

# จักรวาลหนังที่ต้องการดึงอัตโนมัติ
UNIVERSES = [
    {"name": "DCU", "keyword_id": 312528},
    {"name": "MCU", "keyword_id": 180547}
]

def fetch_tv_seasons(tv_id):
    """ดึงข้อมูลทุก Season เพื่อหาวันฉายที่กำลังจะมาถึง"""
    url = f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    seasons = data.get('seasons', [])
    upcoming = []
    
    for s in seasons:
        air_date = s.get('air_date')
        # ตรวจสอบ Season ที่มีวันฉายตั้งแต่วันที่กำหนดไว้
        if air_date and air_date >= START_LOOKBACK:
            upcoming.append({
                "title": f"{data.get('name')} - {s.get('name')}",
                "date": air_date,
                "type": "TV Season"
            })
    return upcoming

def fetch_universe_movies(keyword_id, uni_name):
    """ดึงหนังจากจักรวาลที่ระบุ"""
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_keywords": keyword_id,
        "primary_release_date.gte": START_LOOKBACK,
        "sort_by": "primary_release_date.asc"
    }
    results = requests.get(url, params=params).json().get('results', [])
    return [{"title": f"🎥 [{uni_name}] {m['title']}", "date": m['release_date']} for m in results if m.get('release_date')]

def create_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Superhero & The Boys Tracker//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Marvel, DC, Invincible & The Boys')

    # 1. จัดการซีรีส์ใน Watch List (รวม The Boys และ Invincible SS4)
    for tv in WATCH_LIST_TV:
        for item in fetch_tv_seasons(tv['id']):
            event = Event()
            event.add('summary', f"📺 {item['title']}")
            event.add('dtstart', datetime.datetime.strptime(item['date'], '%Y-%m-%d').date())
            cal.add_component(event)

    # 2. จัดการหนังจาก MCU และ DCU
    for uni in UNIVERSES:
        for m in fetch_universe_movies(uni['keyword_id'], uni['name']):
            event = Event()
            event.add('summary', m['title'])
            event.add('dtstart', datetime.datetime.strptime(m['date'], '%Y-%m-%d').date())
            cal.add_component(event)

    with open('dcu_upcoming.ics', 'wb') as f:
        f.write(cal.to_ical())
    print("Calendar updated successfully with all series and movies!")

if __name__ == "__main__":
    if TMDB_API_KEY:
        create_calendar()
    else:
        print("API Key missing!")
