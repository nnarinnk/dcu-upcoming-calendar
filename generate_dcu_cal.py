# --- แนวคิดโค้ด (generate_dcu_cal.py) ---
import requests
from icalendar import Calendar, Event
import datetime

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY environment variable not set. Please set it in GitHub Secrets.")

DC_STUDIOS_ID = 128064 # Company ID ของ DC Studios (ใช้สำหรับกรองข้อมูล)

# 1. ฟังก์ชันดึงข้อมูลจาก TMDB (ตัวอย่าง: Upcoming Movies)
def fetch_dcu_movies():
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_companies={DC_STUDIOS_ID}&sort_by=primary_release_date.asc"
    response = requests.get(url)
    data = response.json()
    return data.get('results', [])

# 2. ฟังก์ชันสร้างไฟล์ iCal
def create_ical(movies):
    cal = Calendar()
    cal.add('prodid', '-//DCU Calendar//EN')
    cal.add('version', '2.0')

    for movie in movies:
        release_date = movie.get('release_date')
        if release_date:
            event = Event()
            event.add('summary', f"DCU Movie: {movie['title']}")
            
            # แปลงวันที่ให้เป็นวัตถุ Date
            dt_start = datetime.datetime.strptime(release_date, '%Y-%m-%d').date()
            event.add('dtstart', dt_start)
            
            cal.add_component(event)

    # บันทึกไฟล์
    with open('dcu_upcoming.ics', 'wb') as f:
        f.write(cal.to_ical())
        
# 3. รันโปรแกรม
if __name__ == "__main__":
    dcu_data = fetch_dcu_movies()
    create_ical(dcu_data)
