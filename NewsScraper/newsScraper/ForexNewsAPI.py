# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 12:09:25 2019

@author: Novin
"""
import json
import requests
from newsapi.newsapi_client import NewsApiClient
from datetime import datetime, timedelta
import errors

def getForexNews(startDate, endDate):
    try:
        newsapi = NewsApiClient(api_key='caea8ad1719e40e0a08d563ae3405891')
        news = []
        eurusd_articles = newsapi.get_everything(q='eurusd',
                                                 sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                 domains='cnn,bloomberg,reuters,google',
                                                 from_param=startDate,
                                                 to=endDate,
                                                 language='en')
        usdjpy_articles = newsapi.get_everything(q='usdjpy',
                                                 sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                 domains='cnn,bloomberg,reuters,google',
                                                 from_param=startDate,
                                                 to=endDate,
                                                 language='en')

        forex_articles = newsapi.get_everything(q='forex',
                                                sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                domains='cnn,bloomberg,reuters,google',
                                                from_param=startDate,
                                                to=endDate,
                                                language='en')

        oil_articles = newsapi.get_everything(q='oil',
                                              sources='crypto-coins-news,bloomberg,reuters,google-news',
                                              domains='cnn,bloomberg,reuters,google',
                                              from_param=startDate,
                                              to=endDate,
                                              language='en')
        gold_articles = newsapi.get_everything(q='gold',
                                               sources='crypto-coins-news,bloomberg,reuters,google-news',
                                               domains='cnn,bloomberg,reuters,google',
                                               from_param=startDate,
                                               to=endDate,
                                               language='en')

        for item in forex_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'Forex'
            news.append(item)

        for item in eurusd_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'EURUSD'

            news.append(item)

        for item in usdjpy_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'USDJPY'

            news.append(item)
        for item in oil_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'oil'
            news.append(item)
        for item in gold_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'gold'

        news.append(item)
        return (news)

    except ConnectionError:
        raise errors.DataProvidingException(message="Faild to connect google News API", code=2)

    except:
        raise errors.DataProvidingException(message="Faild to fetch news from google News API", code=2)






def JsonItemStandard(newsItem,classifier):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : news provider
    # guid : Guid code
    # pair : explicitly tag by news provider and all the folllowing
    # indicator are based on this pair
    # pivotPoint : Pivot indicator at the time of news release time
    # trendIndex : Trend Index indicator at the news release time
    # ObosIndex : ObosIndex Indicator at the  news release time
    try:

        item = {}
        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['description']
        print(newsItem['publishedAt'])
        # 2020-08-27T01:19:00Z
        currentDate = datetime.strptime(newsItem['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        # print(currentDateString)
        item['pubDate'] = int(currentDate.timestamp())
        item['keywords'] = newsItem['keywords'].lstrip('[').rstrip(']').split(',')
        item['author'] = newsItem['author']
        item['link'] = newsItem['url']
        item['provider'] = newsItem['provider']
        #item['sentiment'], item['sentimentScore'], item['vector'] =predict(item)
        item['thImage'] = newsItem['urlToImage']
        item['summary '] = ''
        results = classifier(item['title'])
        for result in results:
            item['Negative'] = result[0]['score']
            item['neutral'] = result[1]['score']
            item['Positive'] = result[2]['score']

        return item
    except:
        raise errors.DataProvidingException(message="Fail to standard news Item!", code=2)




def saveInMongo1(newsItem,classifier):
    try:

        for item in newsItem:
            item = JsonItemStandard(item,classifier)
            querry = {'link': str(item['link'])}
            # mydoc = mycol.find(querry)
            exist = checkForExist1(querry)
            if not exist:
                # item = JsonItemStandard (item)
                url = 'http://localhost:5000/Robonews/v1/news'
                resp = requests.post(url, json=item)
                print(resp.text)

        print('+---------------------------------------------+')
        return True
    except OSError:
        raise errors.DataProvidingException("Failed to save news in MongoEngine", code=2)
    except :
        raise errors.DataProvidingException("Failed to save news in MongoEngine", code=2)



def checkForExist1(query):
    try:

        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        return resp['data']
    except:
        raise errors.DataProvidingException(message="Failed to check news Existences!", code=2)

def ForexNewsApi(classifier):
    try:

        endDate = datetime.today()
        startDate = datetime.today() - timedelta(days=29)
        # load RSS File From Url
        now = datetime.now()
        print('Crawling of Forex News from API Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
        print('+---------------------------------------------+')
        newsitems = getForexNews(startDate, endDate)
        # store news items in a csv file
        saveInMongo1(newsitems,classifier)
        return  True
    except errors.DataProvidingException as err:
        print("Error : {error} from source number {code} ".format(error=err.message, code=err.code))
    except:
        print("Error : Irregular Error from source number {code} ".format(code=2))




def main():
   ForexNewsApi()

if __name__ == "__main__":

    # calling mpai2n function
    main()

