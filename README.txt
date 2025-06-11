# 📊 Road Accident Counters for Plovdiv

This project automatically collects data about road accidents (ПТП) in Plovdiv from three news websites and displays it on a simple web page. The data is periodically updated and stored in a JSON file.

## 🔗 Data Sources

- [marica.bg](https://www.marica.bg/)
- [plovdiv24.bg](https://www.plovdiv24.bg/)
- [trafficnews.bg](https://trafficnews.bg/)

---

## ⚙️ How It Works

1. `scraper.py` fetches headlines from the three sources and counts accident-related news for:
   - The past **24 hours**
   - The past **7 days**
   - The past **30 days**

2. It saves the statistics in `stats.json`, including:
   - Accident counts (`daily`, `weekly`, `monthly`)
   - Last update timestamp
   - Last seen headline from each site (for debug/verification)

3. `index.html` loads `stats.json` via JavaScript and displays the counters visually using CSS.

---

## 📁 Project Structure

/
├── index.html # Web interface
├── styles.css # Styling
├── scraper.py # Python scraper script
└── stats.json # Data file (auto-updated)

## 🛠️ Installation & Local Setup

1. **Install dependencies:**

```bash
pip install beautifulsoup4 requests schedule

2. Run the scraper manually:
python scraper.py

3.Start a local server to preview the site:
python -m http.server 8000
# Open in browser: http://localhost:8000/index.html


🔐 Note
This project does not collect or display the full content of news articles — only headlines are scanned for accident-related keywords and used for counting.

🕒 Scheduled Updates
Every hour: refresh daily counter

Every day at 08:00: reset 24-hour counter

Every Monday at 08:00: update weekly counter

Every 1st day of the month at 08:00: update monthly counter

