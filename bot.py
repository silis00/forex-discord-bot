import requests
import schedule
import time
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1508519853550469293/7qoc24m2sx3Z14IohCyKc3AW-AKi2YuAt8QPsM4pK-s01djSNbLOJcibSuLt0LBQ6zAp"
NEWS_API_KEY = "24e1ab70b310408ebdf018f7a9875e48"
SENT_FILE = "sent_news.txt"


def load_sent_links():
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()


def save_sent_link(link):
    with open(SENT_FILE, "a", encoding="utf-8") as file:
        file.write(link + "\n")


def send_to_discord(message):
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    if response.status_code == 204:
        print("Messaggio inviato su Discord.")
    else:
        print("Errore Discord:", response.status_code)
        print(response.text)


def get_forex_news():
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": '(forex OR "foreign exchange" OR EURUSD OR GBPUSD OR USDJPY OR USDCHF OR AUDUSD OR NZDUSD OR USDCAD OR XAUUSD OR gold OR FED OR FOMC OR ECB OR BOJ OR "Bank of England" OR inflation OR CPI OR NFP OR "interest rates" OR dollar)',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
       "domains": "forexlive.com,investing.com",
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = data.get("articles", [])
    sent_links = load_sent_links()

    forex_keywords = [
        "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "nzdusd", "usdcad",
        "xauusd", "gold",
        "fed", "fomc", "ecb", "boj", "bank of england",
        "interest rate", "rate hike", "inflation", "cpi",
        "nonfarm payrolls", "nfp",
        "dollar", "forex", "foreign exchange"
    ]

    new_articles = []

    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        link = article.get("url", "")

        content = title + " " + description

        if link and link not in sent_links:
            if any(keyword in content for keyword in forex_keywords):
                new_articles.append(article)

    if not new_articles:
        return None

    message = f"🌍 **FOREX NEWS UPDATE**\n🕒 Ora: {datetime.now().strftime('%H:%M')}\n\n"

    for article in new_articles[:5]:
        title = article.get("title", "Nessun titolo")
        source = article.get("source", {}).get("name", "Fonte sconosciuta")
        link = article.get("url", "")

        message += f"📰 **{title}**\n"
        message += f"📌 Fonte: {source}\n"
        message += f"🔗 {link}\n\n"

        save_sent_link(link)

    message += "⚠️ News automatiche forex/macroeconomiche. Non è un segnale operativo."
    return message


def job():
    hour = datetime.now().hour

    if 6 <= hour < 24:
        print("Cerco nuove news forex...")

        news = get_forex_news()

        if news:
            send_to_discord(news)
        else:
            print("Nessuna nuova news forex da inviare.")
    else:
        print("Fuori orario.")


schedule.every(15).minutes.do(job)

print("Bot Forex News avviato...")

job()

while True:
    schedule.run_pending()
    time.sleep(60)