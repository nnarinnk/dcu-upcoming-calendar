import os
import requests
from icalendar import Calendar, Event
import datetime

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TODAY = datetime.date.today().isoformat()

# รายการแหล่งข้อมูล
UNIVERSES = [
    {"name": "DCU", "keyword_id": 312528},
    {"name": "MCU", "keyword_id": 180547}
]

SPECIFIC_TV_SHOWS = [
    {"name": "Invincible", "id": 95595}
]

def fetch_upcoming(endpoint, keyword_id):
    """ดึงเฉพาะหนัง/ซีรีส์ที่ฉายตั้งแต่วันนี้เป็นต้นไป"""
    url = f"https://api.themoviedb.org/3/discover/{endpoint}"
    date_param = "primary_release_date.gte" if endpoint == "movie" else "first_air_date.gte"
    params = {
        "api_key": TMDB_API_KEY,
        "with_keywords": keyword_id,
        date_param: TODAY, # ดึงเฉพาะอนาคต
        "sort_by": f"{date_param}.asc"
    }
    return requests.get(url, params=params).json().get('results', [])

def fetch_tv_seasons(tv_id):
    """ดึงข้อมูลทุก Season ของซีรีส์เพื่อหาวันฉายในอนาคต"""
    url = f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    seasons = data.get('seasons', [])
    upcoming_seasons = []
    
    for s in seasons:
        air_date = s.get('air_date')
        # กรองเอาเฉพาะ Season ที่จะฉายในอนาคต
        if air_date and air_date >= TODAY:
            upcoming_seasons.append({
                "name": f"{data['name']} - {s['name']}",
                "date": air_date
            })
    return upcoming_seasons

def create_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Superhero Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Marvel, DC & Invincible')

    # 1. ดึงข้อมูล Universe (MCU & DCU)
    for uni in UNIVERSES:
        for m in fetch_upcoming("movie", uni['keyword_id']):
            event = Event()
            event.add('summary', f"🎥 [{uni['name']}] {m['title']}")
            event.add('dtstart', datetime.datetime.strptime(m['release_date'], '%Y-%m-%d').date())
            cal.add_component(event)
            
        for s in fetch_upcoming("tv", uni['keyword_id']):
            event = Event()
            event.add('summary', f"📺 [{uni['name']}] {s['name']}")
            event.add('dtstart', datetime.datetime.strptime(s['first_air_date'], '%Y-%m-%d').date())
            cal.add_component(event)

    # 2. ดึงข้อมูล Invincible (Season 4 และอื่นๆ)
    for show in SPECIFIC_TV_SHOWS:
        for s in fetch_tv_seasons(show['id']):
            event = Event()
            event.add('summary', f"🦸‍♂️ {s['name']}")
            event.add('dtstart', datetime.datetime.strptime(s['date'], '%Y-%m-%d').date())
            cal.add_component(event)

    with open('dcu_upcoming.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"Update completed on {TODAY}")

if __name__ == "__main__":
    if TMDB_API_KEY:
        create_calendar()
