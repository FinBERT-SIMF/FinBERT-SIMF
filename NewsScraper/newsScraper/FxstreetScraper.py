# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020

@author: Novin
"""

# Python code to illustrate parsing of XML files  from fxstreet xml provider
# importing the required modules


import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
# import pandas as pd
from datetime import datetime
# from SentimentAnalysis.predictionModule import predict
import time
import errors


def loadPage(url, fileName=None):
    # url of rss feed
    try:
        # creating HTTP response object from given url
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        resp = requests.get(url, timeout=3, headers=headers)
        fail = 'fail'
        if resp.status_code == 200:
            # saving the xml file
            with open(fileName, 'wb') as f:
                f.write(resp.content)
                f.close()
                return 1
        else:
            with open(fileName, 'wb') as f:
                f.write(bytes(fail.encode()))
                f.close()

                return -1

        resp.close()
        resp.raise_for_status()

    except requests.exceptions.HTTPError as htError:
        print('Http Error: ', htError)
        raise errors.DataProvidingException(message=htError, code=3)
    except requests.exceptions.ConnectionError as coError:
        print('Connection Error: ', coError)
        raise errors.DataProvidingException(message=coError, code=3)
    except requests.exceptions.Timeout as timeOutError:
        print('TimeOut Error: ', timeOutError)
        raise errors.DataProvidingException(message=timeOutError, code=3)

    except requests.exceptions.RequestException as ReError:
        print('Something was wrong: ', ReError)
        raise errors.DataProvidingException(message=ReError, code=3)


def getImageURL(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        img_tags = soup.find_all('img', src=True)

        urls = [img['src'] for img in img_tags]
        return urls
    except:
        raise errors.DataProvidingException(message="Image URL reading Error!", code=3)
        return ' '


def saveAlonePage(url, filename,classifier):
    try:

        description = fxstreetGetPage(url, filename)
        if description is not None and description.get('pubDate') is not None:
            item = JsonItemStandard(description,classifier)
            saveInMongo1(item)
        else:
            print(url)
    except errors.DataProvidingException as err:
        raise errors.DataProvidingException(message=err.message, code=err.code)


def fxstreetGetPage(url, filename):
    try:
        loadPage(url, filename)
        f1 = open('nonScrapedLink.txt', 'a')

        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        description = {}
        if content != 'fail':

            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all("script", id={"SeoApplicationJsonId"})), 'lxml')
            t = str(json_output)
            t = t.replace(' </script>]</p></body></html>', '')
            t = t.replace('<html><body><p>[<script id="SeoApplicationJsonId" type="application/ld+json">', '')
            g = json.loads(t)
            # jsonText = json_output.get_text()
            # jsonData = json.loads(jsonText, strict=False)
            child = g
            description['title'] = child["headline"]
            description['pubDate'] = child["datePublished"]
            description['link'] = child['url']
            description['articleBody'] = child['articleBody']
            if type(child['keywords']) is not str:
                description['keywords'] = child['keywords']
            else:
                description['keywords'] = child['keywords'].rstrip(',').split(',')

            # print( child['keywords'])
            # if len(child['image']) > 0:
            # description['thImage'] = child['image']
            description['thImage'] = ''
            description['author'] = child['author']['name']
            description['summary'] = child["description"]
            description['images'] = child["image"]
            return description
        else:
            f1.write(url)
            f1.write('\n')
            f1.close()
    except  json.JSONDecodeError as err:
        print('read article body error: ', err)
        description['articleBody'] = 'read article body error'
        description['keywords'] = 'read article body error'
        description['author'] = 'read article body error'
        return (description)
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet read articlebidy error", code=3)


def getArticleBody(url, filename):
    try:

        loadPage(url, filename)
        f1 = open('nonScrapedLink.txt', 'a')

        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        description = {}
        if content != 'fail':

            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all("script", id={"SeoApplicationJsonId"})), 'lxml')
            t = str(json_output)
            t = t.replace(' </script>]</p></body></html>', '')
            t = t.replace('<html><body><p>[<script id="SeoApplicationJsonId" type="application/ld+json">', '')
            g = json.loads(t)
            # jsonText = json_output.get_text()
            # jsonData = json.loads(jsonText, strict=False)
            child = g
            for child in g:
                description['articleBody'] = child['articleBody']
                description['keywords'] = child['keywords']
                # print( child['keywords'])
                if len(child['image']) > 0:
                    description['thImage'] = child['image'][0]
                else:
                    description['thImage'] = ''
                description['author'] = child['author']['name']

                description['images'] = getImageURL(content)
            return (description)
        else:
            f1.write(url)
            f1.write('\n')
            f1.close()

    except  json.JSONDecodeError as err:
        print('read article body error: ', err)
        description['articleBody'] = 'read article body error'
        description['keywords'] = 'read article body error'
        description['author'] = 'read article body error'
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet read articlebidy error", code=3)


def parseXML(xmlfile,classifier):
    try:
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        root = tree.getroot()
        # create empty list for news items
        newsitems = []
        # iterate news items
        for item in root:

            for item in item.findall('item'):
                news = {}
                for child in item:
                    if child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}pair':
                        news['pair'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}market':
                        news['market'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}TechAnalysis':
                        for c in child:
                            if c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}TrendIndex':
                                news['TrendIndex'] = c.attrib
                            elif c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}OBOSIndex':
                                news['OBOSIndex'] = c.attrib
                            elif c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}PivotPoints':
                                news['PivotPoints'] = c.attrib

                        news['TechAnalysis'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}headline':
                        news['headline'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}summary':
                        news['summary'] = child.text

                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}provider':
                        news['provider'] = child.text
                    else:
                        news[child.tag] = child.text
                querry = {'link': news['link']}

                exist = checkForExist1(querry)
                if not exist:
                    '''
                    desc = getArticleBody(news['link'], 'articlebody.html')
                    for c in desc:
                        news[c] = desc[c]
                    news = JsonItemStandard(news)

                    saveInMongo1(news)
                    '''
                    saveAlonePage(news['link'], 'articlebody.html',classifier)
                    time.sleep(0.5)

                newsitems.append(news)

                # return news items list
        return newsitems
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet XML reading Errorr", code=3)


def JsonItemStandard(newsItem,classifier):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider
    # sentiment : predictionServices positive/negative
    # predict : predictionServices probability
    try:

        CryptoOtions = {'btcusd', 'bitcoin', 'cryptocurrency',
                        'ethusd', 'etherium', 'crypto', 'xpr',
                        'ripple', 'altcoin', 'crypto'}
        CommoditiesOptions = {'oil', 'gold', 'silver', 'wti', ',brent', 'commodities', 'xauusd', 'metals'}
        item = {}
        # print(item)
        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['articleBody']
        # print(type( newsItem['pubDate']))
        # print( newsItem['pubDate'])
        currentDate = datetime.strptime(newsItem['pubDate'], '%Y-%m-%dT%H:%M:%SZ')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        # item['pubDate'] =  currentDateString
        # currentDate = datetime.strptime(newsItem['pubDate'], '%a, %d %b %Y %H:%M:%S Z')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        # item['pubDate'] = currentDateString
        item['pubDate'] = int(currentDate.timestamp())

        item['keywords'] = newsItem['keywords']
        # print(newsItem['keywords'])
        item['author'] = newsItem['author']
        item['link'] = newsItem['link']
        item['provider'] = 'Fxstreet'
        item['category'] = 'Forex'

        for f in newsItem['keywords']:
            if f.lower() in CryptoOtions:
                item['category'] = 'Cryptocurrency'
                break
        for f in newsItem['keywords']:
            if f.lower() in CommoditiesOptions:
                item['category'] = 'Commodities'
                break

        item['summary'] = newsItem['summary']
        item['thImage'] = newsItem['thImage']
        item['images'] = newsItem['images']
        results = classifier(item['title'] )

        for result in results:
            item['Negative'] = result[0]['score']
            item['neutral'] = result[1]['score']
            item['Positive'] = result[2]['score']

        return item
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXSTREET standardization error", code=3)


def checkForExist1(query):
    try:

        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        return resp['data']
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=3)
    except:
        raise errors.DataProvidingException(message="Error in saving to mongoengine", code=3)


def saveInMongo1(item):
    try:

        url = 'http://localhost:5000/Robonews/v1/news'
        # items = json.dumps(item)
        resp = requests.post(url, json=item)
        print(resp.text)
        return
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=3)
    except:
        raise errors.DataProvidingException(message="Failed to save in Mongoengine", code=3)


def fxstreetScraper(classifier):
    try:
        f = open('Forexlog.txt', 'a')
        url = 'http://xml.fxstreet.com/news/forex-news/index.xml'
        filename = 'topnewsfeed.xml'
        # load RSS File From Url
        now = datetime.now()
        print('crawling of fxstreet Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
        print('+---------------------------------------------+')

        code = loadPage(url, filename)
        if code == 1:
            parseXML(filename,classifier)
            print('+---------------------------------------------+')
        # store news items in a csv file
        else:
            f.write('Connection Error at time : ' + datetime.now().strftime('%y %m %d %H %M %S') + '\n')
            f.close()
    except errors.DataProvidingException as err:
            print("Error : {error} from source number {code} ".format(error=err.message, code=err.code))
    except:
        print("Error : Irregular Error from source number {code} ".format(code=2))


def crawlOldNews():
    filename = "url.txt"
    f = open(filename, 'r')
    urlList = f.readlines()
    i = 0
    for item in urlList:
        if item.find('fxstreet'):
            saveAlonePage(item.strip(), 'articlebody.html')
            print(i)
            i = i + 1
    return


def main():
    # exportForexCSV ()
    fxstreetScraper()
    return


if __name__ == "__main__":
    # calling mpai2n function
    main()
