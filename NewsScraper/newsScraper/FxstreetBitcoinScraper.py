# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020

@author: Novin
"""

# Python code to illustrate directly parsing the news page with beautifulsoap python package

# importing the required modules
import errors
import requests, re
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
import errors


def loadPage(url, fileName=None):
    # todo : change t,replace in getarticleBody
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



def getArticleBody(url, filename='None'):

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

                description['images'] = child['image']
                description['summary'] = child['description']
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
        raise errors.DataProvidingException(message="FXstreet read articlebody error", code=3)



# remove tags regular expression
def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


def parseXML(filename,classifier):
    try:

        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        description = []
        if content != 'fail':

            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all("script", type={"application/ld+json"})), 'lxml')
            t = str(json_output)
            t = remove_tags(t)
            g = json.loads(t)

            for child in g:
                if 'headline' in child:
                    saveAlonePage(child['url'], 'item.html',classifier)
            return True
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet XML reading Errorr", code=3)





def fxstreetGetPage(url, filename):
    loadPage(url, filename)
    f1 = open('nonScrapedLink.txt', 'a')
    try:

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


def saveAlonePage(url, filename,classifier):
    description = fxstreetGetPage(url, filename)
    if description is not None and description.get('pubDate') is not None:
        item = JsonItemStandard(description)
        saveInMongo1(item)
    else:
        print(url)


def checkForExist1(query):
    url = 'http://localhost:5000/Robonews/v1/news'
    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    return resp['data']


def saveInMongo1(item):
    url = 'http://localhost:5000/Robonews/v1/news'
    # items = json.dumps(item)
    resp = requests.post(url, json=item)
    print(resp.text)


def JsonItemStandard(newsItem,classifier):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider
    CryptoOtions = ['btcusd', 'bitcoin', 'cryptocurrency','cryptocurrencies',
                    'ethusd', 'etherium', 'crypto', 'xpr',
                    'ripple', 'altcoin', 'crypto']
    CommoditiesOptions = ['oil', 'gold', 'silver', 'wti', ',brent', 'commodities', 'xauusd', 'metals']
    item = {}
    item['title'] = newsItem['title']
    item['articleBody'] = newsItem['articleBody']
    # currentDate = datetime.strptime(newsItem['pubDate'], '%m/%d/%Y %I:%M:%S %p')
    currentDate = datetime.strptime(newsItem['pubDate'], '%Y-%m-%dT%H:%M:%SZ')
    item['pubDate'] = int(currentDate.timestamp())
    # keywords = [w.lower() for w in newsItem['keywords']]
    print(newsItem['keywords'])
    item['keywords'] = newsItem['keywords']
    # item['keywords'] = keywords
    item['author'] = newsItem['author']
    item['link'] = newsItem['link']
    item['provider'] = 'FXstreet CryptoCurrency'
    # item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
    item['summary'] = ''
    item['thImage'] = newsItem['thImage']
    item['images'] = newsItem['images']
    item['category'] = 'Forex'
    for f in newsItem['keywords']:
        if f.lower() in CryptoOtions:
            item['category'] = 'Cryptocurrency'
            break
    else:
        for f in newsItem['keywords']:
            if f.lower() in CommoditiesOptions:
                item['category'] = 'Commodities'
                break
    results = classifier(item['title'])
    for result in results:
        item['Negative'] = result[0]['score']
        item['neutral'] = result[1]['score']
        item['Positive'] = result[2]['score']



    return item


def fxstreetBitcoinScraper(classifier):
    try:
        f = open('Forexlog.txt', 'a')
        url = 'https://www.fxstreet.com/cryptocurrencies/news'
        filename = 'topnewsfeed.html'
        # load RSS File From Url
        now = datetime.now()
        print('crawling of fxstreet for Crypocurrencies Started ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
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

def main():
    fxstreetBitcoinScraper()


if __name__ == "__main__":
    # calling mpai2n function
    main()
