# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020
Crawl cryptocurrencies news from cointelegraph.
I use rss of all coins news
@author: Novin
"""

# Python code to illustrate parsing of XML files  from fxstreet xml provider
# importing the required modules


import requests
import json,re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
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
        raise errors.DataProvidingException(message=htError, code=4)

    except requests.exceptions.ConnectionError as coError:
        print('Connection Error: ', coError)
        raise errors.DataProvidingException(message=coError, code=4)

    except requests.exceptions.Timeout as timeOutError:
        print('TimeOut Error: ', timeOutError)
        raise errors.DataProvidingException(message=timeOutError, code=4)

    except requests.exceptions.RequestException as ReError:
        print('Something was wrong: ', ReError)
        raise errors.DataProvidingException(message=ReError, code=4)


def getImageURL(content):
    try:

        soup = BeautifulSoup(content, 'html.parser')
        img_tags = soup.find_all('img', src=True)

        urls = [img['src'] for img in img_tags]
        return urls[0]
    except:
        raise errors.DataProvidingException(message="Image URL reading Error!", code=4)
        return ' '


# remove tags regular expression
def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)

def getArticleBody(url, filename):

    try:
        loadPage(url, filename)
        f1 = open('nonScrapedLink.txt', 'a')
        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        description = {}
        if content != 'fail':
            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all
                                            (lambda tag: tag.name == 'div' and tag.get('class')
                                                         == ['post-content'])), "lxml")

            jsonText = json_output.get_text()
            description = str(jsonText)
            return (description)
        else:
            f1.write(url)
            f1.write('\n')
            f1.close()


    except  json.JSONDecodeError as err:
        raise errors.DataProvidingException(message=err.message, code=4)
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet read articlebidy error", code=4)



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
                category = {}
                for child in item:
                    if child.tag == '{http://purl.org/dc/elements/1.1/}creator':
                        news['author'] = child.text.replace('Cointelegraph By ', '')
                    elif child.tag == 'category':
                        category['item{}'.format(len(category) + 1)] = child.text
                    elif child.tag == 'description':
                        news['thImage'] = getImageURL(child.text)
                        news['summary'] = child.text


                    else:
                        news[child.tag] = child.text
                news['category'] = category
                querry = {'link': news['link']}

                exist = checkForExist1(querry)
                if not exist:
                    news['articleBody'] = getArticleBody(news['link'], 'articlebody.html')
                    #print(news)
                    news = JsonItemStandard(news,classifier)

                    saveInMongo1(news)
                    time.sleep(0.5)

                newsitems.append(news)

                # return news items list
        return newsitems
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="Cointelegraph XML reading Errorr", code=4)


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

        item = {}

        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['articleBody']
        newsItem['pubDate'] = newsItem['pubDate'][:-6]
        currentDate = datetime.strptime(newsItem['pubDate'], '%a, %d %b %Y %H:%M:%S')
        item['pubDate'] = int(currentDate.timestamp())
        item['keywords'] = list(newsItem['category'].values())
        # item['keywords'] = keywords
        item['author'] = newsItem['author']
        item['link'] = newsItem['link']
        item['provider'] = 'cointelegraph'
        item['category'] = 'Cryptocurrency'
        # todo : check for summary
        item['summary'] = ''
        item['thImage'] = newsItem['thImage']
        item['images'] = ''
        results = classifier(item['title'])
        item['sentiment'] = results['label']
        if results['label'] == "NEGATIVE":
            item['sentimentScore'] = -1 * results['score']
        else:
            item['sentimentScore'] = results['score']
        if item['pubDate'] is None:
            raise errors.DataProvidingException(message="Cointelegraph standardization error", code=4)
        results = classifier(item['title'])
        for result in results:
            item['Negative'] = result[0]['score']
            item['neutral'] = result[1]['score']
            item['Positive'] = result[2]['score']
        return item
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="Cointelegraph standardization error", code=4)



def checkForExist1(query):
    try:

        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        return resp['data']
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=4)
    except:
        raise errors.DataProvidingException(message="Cointelegraph: Error in saving to mongoengine", code=4)


def saveInMongo1(item):
    try:
        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.post(url, json=item)
        print(resp.text)
        return
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=4)
    except:
        raise errors.DataProvidingException(message="Failed to save in Mongoengine", code=4)


def cointelegraphScraper(classifier):
    try:
        f = open('Forexlog.txt', 'a')
        url = 'https://cointelegraph.com/rss'

        filename = 'topnewsfeed.xml'
        # load RSS File From Url
        now = datetime.now()
        print('crawling of cointelegraph Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S') + '!!')
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
        print("Error : Irregular Error from source number {code} ".format(code=4))



def main():


    cointelegraphScraper()
    return
if __name__ == "__main__":

    # calling mpai2n function
    main()
