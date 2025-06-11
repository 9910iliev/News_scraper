import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import schedule
import time
import os

DATA_FILE = "scraped_data.json"
HTML_FILE = "index.html"
STATS_FILE = "stats.json"

# --- SCRAPE ФУНКЦИИ ---

def scrape_marica():
    url = "https://www.marica.bg/"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [a.get_text(strip=True) for a in soup.select("a.news-item__title")]
        return titles
    except Exception as e:
        print(f"Грешка в scrape_marica: {e}")
        return []

def scrape_plovdiv24():
    url = "https://www.plovdiv24.bg/"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [a.get_text(strip=True) for a in soup.select("a.news-link")]
        return titles
    except Exception as e:
        print(f"Грешка в scrape_plovdiv24: {e}")
        return []

def scrape_trafficnews():
    url = "https://trafficnews.bg/"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [h2.get_text(strip=True) for h2 in soup.select("h2.title")]
        return titles
    except Exception as e:
        print(f"Грешка в scrape_trafficnews: {e}")
        return []

def scrape_all():
    titles = []
    titles.extend(scrape_marica())
    titles.extend(scrape_plovdiv24())
    titles.extend(scrape_trafficnews())
    return titles

# --- ФИЛТЪР ---

def filter_ptp_plovdiv(titles):
    filtered = []
    for t in titles:
        t_lower = t.lower()
        if ("птп" in t_lower or "катастрофа" in t_lower or "пътно-транспортно" in t_lower) and "пловдив" in t_lower:
            filtered.append(t)
    return filtered

# --- ДАННИ ---

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_data(existing_data, new_titles):
    now_str = datetime.now().isoformat()
    existing_texts = {item['title'] for item in existing_data}
    added = 0
    for title in new_titles:
        if title not in existing_texts:
            existing_data.append({"title": title, "timestamp": now_str})
            added += 1
    print(f"Добавени нови новини: {added}")
    return existing_data

def count_in_period(data, delta):
    cutoff = datetime.now() - delta
    count = 0
    for item in data:
        try:
            item_time = datetime.fromisoformat(item['timestamp'])
            if item_time >= cutoff:
                count += 1
        except Exception:
            pass
    return count

# --- ЗАПИС НА JSON СТАТИСТИКИ ---

def save_stats_json(daily, weekly, monthly, last_update):
    stats = {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "last_update": last_update
    }
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# --- RESET ФУНКЦИИ ---

def reset_daily():
    data = load_data()
    cutoff = datetime.now() - timedelta(days=1)
    data = [item for item in data if datetime.fromisoformat(item['timestamp']) >= cutoff]
    save_data(data)
    print("Ресетнато за 24 часа")

def reset_weekly():
    data = load_data()
    cutoff = datetime.now() - timedelta(days=7)
    data = [item for item in data if datetime.fromisoformat(item['timestamp']) >= cutoff]
    save_data(data)
    print("Ресетнато за седмица")

def reset_monthly():
    data = load_data()
    cutoff = datetime.now() - timedelta(days=30)
    data = [item for item in data if datetime.fromisoformat(item['timestamp']) >= cutoff]
    save_data(data)
    print("Ресетнато за месец")

def reset_monthly_workaround():
    now = datetime.now()
    if now.day == 1 and now.hour == 8 and now.minute == 0:
        reset_monthly()

# --- ОСНОВНА ФУНКЦИЯ ---

def job():
    print(f"\n=== Стартира scrape: {datetime.now()} ===")
    data = load_data()

    all_titles = scrape_all()
    filtered = filter_ptp_plovdiv(all_titles)
    data = update_data(data, filtered)
    save_data(data)

    daily_count = count_in_period(data, timedelta(days=1))
    weekly_count = count_in_period(data, timedelta(days=7))
    monthly_count = count_in_period(data, timedelta(days=30))

    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats_json(daily_count, weekly_count, monthly_count, last_update)

# --- ПЛАНИРАНЕ ---

import schedule
import time

schedule.every().hour.at(":00").do(job)
schedule.every().day.at("08:00").do(reset_daily)
schedule.every().monday.at("08:00").do(reset_weekly)
schedule.every().minute.do(reset_monthly_workaround)

job()

while True:
    schedule.run_pending()
    time.sleep(30)
