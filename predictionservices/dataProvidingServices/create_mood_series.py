from typing import Tuple, Dict, List

import pandas as pd
import logging
import requests
import time
import datetime
from dateutil.tz import tzutc
import os

from definitions import ROOT_DIR
from dataProvidingServices.dataProviding import load_news

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

API_TOKEN = ...  # INSERT YOUR TOKEN HERE
API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def query_sentiment(text: List[str]) -> Dict[str, str]:
    return query(
        {"inputs": text}
    )


def query_finbert(news: pd.DataFrame, from_index: int = None, batch_size: int = 100) -> Tuple[pd.DataFrame, int]:
    logging.info(f"Starting querying sentiment from index {from_index}.")

    column2index = {label: news.columns.get_loc(label) for label in news.columns}
    assert column2index['positive'] == 3

    save_path = 'mood.csv'

    continue_at_index = 0
    count = 0
    for index in range(from_index, news.shape[0], batch_size):
        continue_at_index = index

        title = news.iloc[index, 0] # title
        # fetch batch_size number of titles
        titles = (
            news
            .iloc[index:index+batch_size, column2index['title']]
            .values
            .tolist()
        )

        logging.debug(f"from {index=} to {(index+batch_size)=}, {titles[0][:10]=}")

        all_sentiments = query_sentiment(titles)

        if isinstance(all_sentiments, dict) and 'error' in all_sentiments: # if failed
            logging.debug(all_sentiments['error'])

        assert isinstance(all_sentiments, list)

        # iterate over batch
        for index_offset, sentiments in enumerate(all_sentiments):
            # insert sentiment in news dataframe
            for sentiment in sentiments:
                news.iloc[index + index_offset, column2index[sentiment['label']]] = sentiment['score']

            count += 1

        logging.info(f"Sucessfully queried sentiments. {count=}")

        # checkpoint every 10th batch
        if index % 1000 == 0:
            logging.info(f"Saving to {save_path}")
            news.to_csv(save_path, sep='\t')

    logging.info(f'Successfully fetched {count} sentiment samples.')
    logging.info(f"Current total number of sentiments: {news['neutral'].notna().sum()}")
    return news, continue_at_index


def populate_sentiments(news, from_index=0):
    logging.debug(f"Starting from index {from_index}")

    while from_index <= news.shape[0]:
        news, from_index = query_finbert(news, from_index)

        logging.debug("Waiting until next query session")
        time.sleep(60)

        if from_index == news.index[-1]:
            logging.debug(f"{from_index} == {news.index[-1]}, finishing...")
            break

    logging.debug(f"Finished populating sentiments: current total {news['neutral'].notna().sum()}")
    return news, from_index


def compute_mood_series() -> None:
    """Compute sentiment score for news time series.

    :param news_df: dataframe with news titles, bodies and timestamps
    :return: new_S: dataframe with sentiment scores and timestamps
    """
    category = 'Forex'
    pair = 'EURUSD'
    news_keywords = 'EURUSD'
    start_date = datetime(2018, 9, 21, 16, 34, 4, tzinfo=tzutc())
    end_date = datetime(2021, 5, 4, 7, 2, 36)
    training = True
    save_path = os.path.join(ROOT_DIR, "data", "mood.csv")

    # load data
    news_df = load_news(category, news_keywords, start_date, end_date, training)

    # fetch mood
    mood = populate_sentiments(news_df)

    logging.info(f"{mood['neutral'].notna().sum()}")
    logging.info(f"Done fetching sentiments, saving to {save_path}")

    # save final dataframe
    mood.to_csv(save_path, sep=r'\t')
    print(mood)


if __name__ == "__main":
    compute_mood_series()