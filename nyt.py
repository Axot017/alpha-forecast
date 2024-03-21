from datetime import date
import requests
import csv
import os
import time
import pandas as pd
from dotenv import load_dotenv


BASE_URL = "https://api.nytimes.com"
LAST_DATE = date(1990, 1, 1)

load_dotenv()


def get_articles_for_month(year, month, token):
    url = f"{BASE_URL}/svc/archive/v1/{year}/{month}.json"
    params = {"api-key": token}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def extract_relevant_info(articles):
    articles = articles["response"]["docs"]

    for article in articles:
        headline = article["abstract"]
        lead_paragraph = article["lead_paragraph"]
        date = article["pub_date"]
        yield {"date": date, "headline": headline, "lead_paragraph": lead_paragraph}


def write_to_csv(articles, filename):
    with open(filename, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["date", "headline", "lead_paragraph"]
        )
        writer.writeheader()
        writer.writerows(articles)


def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_previous_month(date):
    if date.month == 1:
        return date.replace(year=date.year - 1, month=12)

    return date.replace(month=date.month - 1)


def get_next_month(date):
    if date.month == 12:
        return date.replace(year=date.year + 1, month=1)

    return date.replace(month=date.month + 1)


def process_month(token, date):
    year = date.year
    month = date.month
    print(f"Processing {year}-{month:02d}")
    articles = get_articles_for_month(year, month, token)
    articles = extract_relevant_info(articles)
    write_to_csv(articles, f"out/nyt/{year}-{month:02d}.csv")


def get_newest_processed_date():
    files = os.listdir("out/nyt")
    if not files:
        return None

    last_file = sorted(files)[-1]
    # Last entry in this file
    last_entry = pd.read_csv(f"out/nyt/{last_file}").iloc[-1]
    date = last_entry["date"]

    return pd.to_datetime(date).date()


def get_old_processed_date():
    files = os.listdir("out/nyt")
    if not files:
        return None

    last_file = sorted(files)[0]
    # Last entry in this file
    last_entry = pd.read_csv(f"out/nyt/{last_file}").iloc[0]
    date = last_entry["date"]

    return pd.to_datetime(date).date()


def is_same_month_or_before(date1, date2):
    if date1.year < date2.year:
        return True
    if date1.year == date2.year and date1.month <= date2.month:
        return True

    return False


def fetch_articles():
    make_dir_if_not_exists("out/nyt")
    token = os.getenv("NYT_API_KEY")

    print(f"Newest processed date: {get_newest_processed_date()}")
    print(f"Oldest processed date: {get_old_processed_date()}")

    now = date.today().replace(day=1)
    newest_processed_date = get_newest_processed_date()
    # process until now
    while newest_processed_date is not None and is_same_month_or_before(
        newest_processed_date, now
    ):
        process_month(token, newest_processed_date)
        newest_processed_date = get_next_month(newest_processed_date)
        time.sleep(12)

    oldest_processed_date = get_old_processed_date()

    if oldest_processed_date is None:
        oldest_processed_date = now

    if (
        oldest_processed_date.year <= LAST_DATE.year
        and oldest_processed_date.month <= LAST_DATE.month
    ):
        return

    while True:
        process_month(token, oldest_processed_date)
        oldest_processed_date = get_previous_month(oldest_processed_date)
        time.sleep(12)


if __name__ == "__main__":
    fetch_articles()
