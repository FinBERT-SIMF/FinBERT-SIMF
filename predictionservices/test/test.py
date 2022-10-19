from datetime import datetime
from dateutil.tz import tzutc
import logging

from dataProvidingServices.dataProviding import (
    load_training_data,
    load_market_data,
    load_news,
    transform_market_data
)

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def test_transform_market_data(category, pair, start_date, end_date, training,
                               resolution, sequence_length):
    market_df, _, _ = load_market_data(category, pair, start_date, end_date, training, resolution, sequence_length)

    market_df_transformed = transform_market_data(market_df, training, sequence_length)
    print(market_df_transformed.describe())
    print(market_df_transformed)


def test_load_market_data(category, pair, start_date, end_date, training,
                          resolution, sequence_length):
    """Test for loading market data from Excel file"""
    market_df = load_market_data(category, pair, start_date, end_date, training, resolution, sequence_length)
    print(market_df)


def test_load_news(category, news_keywords, start_date, end_date, training):
    """Test for loading news from Excel file"""
    news = load_news(category=category, news_keywords=news_keywords,
                     start_date=start_date, end_date=end_date, Long=training)

    print(news)


def test_load_training_data_eurusd(category, pair, news_keywords,
                                   start_date, end_date,
                                   resolution, sequence_length,
                                   training, query):
    # s = datetime.utcnow().timestamp()
    # three_years_ts = 94867200
    # e = s - three_years_ts
    load_training_data(category, pair, start_date, end_date,
                       news_keywords, resolution=resolution, sequence_length=sequence_length,
                       training=training, query=query)


def main() -> None:
    category = 'Forex'
    pair = 'EURUSD'
    news_keywords = 'EURUSD'
    start_date = datetime(2018, 9, 21, 16, 34, 4, tzinfo=tzutc())
    end_date = datetime(2021, 5, 4, 7, 2, 36)
    training = True
    query = False
    sequence_length = 7
    resolution = 60

    # test_load_market_data(category, news_keywords, start_date, end_date, training, resolution, sequence_length)
    # test_load_training_data_eurusd(category=category, pair=pair, news_keywords=news_keywords,
    #                                start_date=start_date, end_date=end_date,
    #                                resolution=resolution, sequence_length=sequence_length,
    #                                training=training, query=query)
    test_transform_market_data(category, pair, start_date, end_date, training, resolution, sequence_length)
    # test_load_news(category=category, news_keywords=news_keywords,
    #                start_date=start_date, end_date=end_date, Long=training)


if __name__ == "__main__":
    main()