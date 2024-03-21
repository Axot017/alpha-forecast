import requests
from dotenv import load_dotenv
import os

BASE_URL = "https://query1.finance.yahoo.com"
DOWNLOAD_PATH = "/v7/finance/download"

PARAMS = {
    "period1": "0",
    "period2": "4077807061",
    "interval": "1d",
    "events": "history",
    "includeAdjustedClose": "true",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

load_dotenv()


def fetch_data(symbol):
    return requests.get(
        f"{BASE_URL}{DOWNLOAD_PATH}/{symbol}",
        params=PARAMS,
        headers=HEADERS,
    )


def fetch_crypto(symbol):
    return fetch_data(f"{symbol}-USD")


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_data(path, symbol, data):
    create_dir(path)
    with open(f"{path}/{symbol}.csv", "w") as f:
        f.write(data.text)


def fetch_all_stocks():
    symbols = os.getenv("STOCKS")
    if symbols is None:
        return
    symbols = symbols.split(",")

    for symbol in symbols:
        data = fetch_data(symbol)
        save_data("out/stock", symbol, data)


def fetch_all_crypto():
    symbols = os.getenv("CRYPTOS")
    if symbols is None:
        return
    symbols = symbols.split(",")

    for symbol in symbols:
        data = fetch_crypto(symbol)
        save_data("out/crypto", symbol, data)


def fetch_all():
    fetch_all_stocks()
    fetch_all_crypto()


if __name__ == "__main__":
    fetch_all()
