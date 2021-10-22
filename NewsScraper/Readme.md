## News Scraping Service

This service automaticaly connected to the specialized financial news groupes every 60 minutes with scaduler module and scrap the latest news. Then store all scraped news into MongoDB dataset.

For installation :

pip install 

python run main.py

#### Currenly available resources are:

 -  [FXStreet](https://www.fxstreet.com/news) for Forex currency pairs news scraping
 - [FXStreet Cryptocurrency Section](https://www.fxstreet.com/cryptocurrencies/news) for cryptocurrencies news scraping
 - [NewsBTC](https://www.newsbtc.com/) for cryptocurrencies news scraping
 - [cointelegraph](https://cointelegraph.com/) for cryptocurrencies news scraping
 - [Investing](https://www.investing.com/) for commodities news scraping (Gold, Metals, Oil, Gas)
 - [Google News API]() for scraping the latest news from specialized newsgroups such as Reuters or Bloomberg. I did scraping of all news about Forex and cryptocurrencies market.
 

After scraping, we statndard all scraped news based on following attributes. All news items store in **one** MongoDB collection. For each item in our news collection, we have following attributes:

| Attribute | Description | Example | Null |
|-----------|-------------|--------|--------|
|   ID      | News ID     | 5f2d88d22222N7db5e8abe014 |No|
|   title   | News Title. |    Canada: Will impose tariffs on imports of certain US aluminum products by September 6|No|
|   body   | News body | USD stronger ahead of the weekly close, although the movement seems corrective.   |Yes|
|   pubDate| News release time based GMT timezone |  Sat, 23 Jan 2021 16:01:31 Z. All news items have the same date/time formating '%a, %d %b %Y %H:%M:%S Z'|No|
|   author   | News author | Valeria Bednarik   | No |
|   keywords  | News keywords. | Sentiment,EURUSD,Employment,Recommended,Coronavirus,   |No| 
   category      | News category     | `Forex`, `Cryptocurrency`, `Commodities`|No|
|   provider      | Newsgroup    | FXStreet, newsBTC, Reuters, Cointelegraph, Investing, Bloomberg|
|   summary      | news summary     | A breif summary about news|Yes|
|   link      | News link     |https://www.fxstreet.com/news/eur-usd-turkey-risks-could-trigger-overdue-correction-lower-for-the-euro-mufg-202008071657 |No|
|   Sentiment Score      |  DistilBERT Sentiment Score    | [-1,1] |No
|   Sentiment |  Sentiment class    | Positive/Negative |Yes. 
|   thImage      | URL of news thumbnail image     | URL of news thumbnail image | Yes
|    images | URLs of images in news body    |  Array of URLs of news images  |No

### Some tips:

 - For news scraping with Google News API, we have limited access to 12 calls per day.  Therefore, I used it within daily scheduling.
 - For some resources such as Cointelegraph, Google News API the news provider did not prepare a keywords list. Thus, I manually determine the news keywords based on occurrences of some known terms such as 'bitcoin' or 'EURUSD' and etc. 
 -  For all newsgroups, I used RSS feed link except FXStreet cryptocurrencies news, which I used direct link scraping of the corresponding [page](https://www.fxstreet.com/cryptocurrencies/news).
  
 - Sentiment analysis is done based on Pre-trained DistilBERT-based-uncased version. 
 
 
