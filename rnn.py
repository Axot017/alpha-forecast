import pandas as pd
import numpy as np
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input,
    LSTM,
    Dense,
    Embedding,
    concatenate,
    Flatten,
    BatchNormalization,
    Dropout,
)
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler


def clean_text(text):
    text = re.sub(r"[^a-zA-Z\s]", "", text, re.I | re.A)
    text = text.lower()
    text = text.strip()

    return text


def load_news():
    print("Loading news data")
    news = pd.read_csv("out/nyt/2020-01.csv")
    news["date"] = pd.to_datetime(news["date"]).dt.date

    news["headline"] = news["headline"].astype(str).apply(clean_text)
    news["lead_paragraph"] = news["lead_paragraph"].astype(str).apply(clean_text)
    news["text"] = news["headline"] + " " + news["lead_paragraph"]

    filtered_news = news[
        (news["headline"].apply(lambda x: len(x) >= 30))
        & (news["lead_paragraph"].apply(lambda x: len(x) >= 30))
    ]

    print("News data loaded")
    return filtered_news


def load_stocks(stock):
    print("Loading stock data")
    stocks = pd.read_csv(f"out/stock/{stock}.csv")
    stocks["Date"] = pd.to_datetime(stocks["Date"]).dt.date
    date_range = pd.date_range(
        start=stocks["Date"].iloc[0], end=stocks["Date"].iloc[-1]
    )
    date_df = pd.DataFrame(date_range.date, columns=["Date"])
    merged = pd.merge(date_df, stocks, on="Date", how="left")
    merged.ffill(inplace=True)
    print("Stock data loaded")
    merged["PrevClose"] = merged["Close"].shift(1)
    merged["Return"] = (merged["Close"] - merged["PrevClose"]) / merged["PrevClose"]

    return merged


def first_stock_entry(stocks):
    return stocks["Date"].iloc[0]


def first_news_entry(news):
    return news["date"].iloc[0]


def skip_frames_to_date_match(news, stocks):
    stock_date = first_stock_entry(stocks)
    news_date = first_news_entry(news)
    if news_date < stock_date:
        news = news[news["date"] >= stock_date]
        news.reset_index(drop=True, inplace=True)
    elif news_date > stock_date:
        stocks = stocks[stocks["Date"] >= news_date]
        stocks.reset_index(drop=True, inplace=True)
    return news, stocks


def print_data(news, stocks):
    print("News data:")
    print(news.head())
    print("Stock data:")
    print(stocks.head())


def tokenize_text(news_df, num_words=1000, max_len=100):
    print("Tokenizing text")
    tokenizer = Tokenizer(num_words=num_words, oov_token="<OOV>")
    tokenizer.fit_on_texts(news_df["text"])
    print("Tokenizer fitted")

    print("Padding sequences")
    sequences = tokenizer.texts_to_sequences(news_df["text"])
    padded = pad_sequences(sequences, maxlen=max_len, padding="post", truncating="post")
    print("Sequences padded")

    return padded, tokenizer


def scale_stocks(stocks):
    print("Scaling stocks")
    scaler = StandardScaler()
    stocks_features = ["Open", "High", "Low", "Close", "Volume", "Return"]

    scaled = scaler.fit_transform(stocks[stocks_features])

    print("Stocks scaled")

    return scaled, scaler


def main():
    news = load_news()
    stocks = load_stocks("AAPL")
    news, stocks = skip_frames_to_date_match(news, stocks)
    print_data(news, stocks)
    padded, tokenizer = tokenize_text(news)
    scaled_stocks, scaler = scale_stocks(stocks)

    vocab_size = len(tokenizer.word_index) + 1
    embedding_dim = 50
    text_sequence_length = 100
    num_stocks_features = scaled_stocks.shape[1] - 1

    text_input = Input(shape=(text_sequence_length,), name="text_input", dtype="int32")
    embedded_text = Embedding(vocab_size, embedding_dim)(text_input)
    lstm_out = LSTM(64)(embedded_text)

    stock_input = Input(shape=(num_stocks_features,), name="stock_input")
    dense_num_1 = Dense(32, activation="relu")(stock_input)
    bn_num_1 = BatchNormalization()(dense_num_1)
    dropout_num_1 = Dropout(0.5)(bn_num_1)

    merged = concatenate([lstm_out, dropout_num_1], axis=-1)
    dense_merged_1 = Dense(64, activation="relu")(merged)
    bn_merged_1 = BatchNormalization()(dense_merged_1)
    dropout_merged_1 = Dropout(0.5)(bn_merged_1)
    output = Dense(1, activation="sigmoid")(dropout_merged_1)

    model = Model(inputs=[text_input, stock_input], outputs=output)
    model.compile(optimizer=Adam(), loss="binary_crossentropy", metrics=["accuracy"])

    model.summary()

    padded_list = padded.tolist() if isinstance(padded, np.ndarray) else padded

    news_df = pd.DataFrame({"date": news["date"].tolist(), "padded_text": padded_list})

    grouped = news_df.groupby("date")["padded_text"].apply(
        lambda x: np.mean(np.vstack(x), axis=0).tolist()
    )
    aggregated = pd.DataFrame(grouped).reset_index()


if __name__ == "__main__":
    main()
