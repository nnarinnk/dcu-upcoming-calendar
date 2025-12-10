# --- แนวคิดโค้ด (generate_dcu_cal.py) ---
import os
import requests
from icalendar import Calendar, Event
import datetime
from datetime import date

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY environment variable not set. Please set it in GitHub Secrets.")

DC_COMPANY_IDS = "128064|9993"

# 1. ฟังก์ชันดึงข้อมูลจาก TMDB (ตัวอย่าง: Upcoming Movies)
def fetch_dcu_movies():
    # หาวันที่ปัจจุบัน รูปแบบ YYYY-MM-DD
    today = date.today().strftime("%Y-%m-%d")
    
    # เพิ่ม primary_release_date.gte เพื่อเอาเฉพาะหนังในอนาคต
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_companies={DC_COMPANY_IDS}&sort_by=primary_release_date.asc&primary_release_date.gte={today}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

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
