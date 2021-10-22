# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 07:21:47 2021

@author: Novin
"""

# Python code to illustrate parsing of XML files  from fxstreet xml provider
# importing the required modules


import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
import re
import errors

def cleanText(sen):
    try:
    # lowercase
        sen = sen.lower()
        # remove tag
        sentence = re.sub(r'<[^>]+>', ' ', sen)
        # remove url from sentence
        sentence = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|-)*\b',
                          '', sen)
        # Remove punctuations and numbers
        sentence = re.sub('[^a-zA-Z]', ' ', sentence)
        # Single character removal
        sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)
        # Removing multiple spaces
        sentence = re.sub(r'\s+', ' ', sentence)

        return sentence
    except:
        raise errors.DataProvidingException(message="Investing errors in news preprocessing",code=6)


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
        raise errors.DataProvidingException(message=htError, code=7)
    except requests.exceptions.ConnectionError as coError:
        print('Connection Error: ', coError)
        raise errors.DataProvidingException(message=coError, code=7)
    except requests.exceptions.Timeout as timeOutError:
        print('TimeOut Error: ', timeOutError)
        raise errors.DataProvidingException(message=timeOutError, code=7)

    except requests.exceptions.RequestException as ReError:
        print('Something went wrong for loading news: ', ReError)
        raise errors.DataProvidingException(message=ReError, code=7)

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
            result = soup.findAll(attrs={'class': re.compile(r"^WYSIWYG articlePage$")})
            jsonText = ''
            articlebody = ''
            for ele in result:
                # print(ele)
                articlebody += ele.get_text()
                jsonText += ele.get_text()
            description['articleBody'] = str(articlebody)
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
        return description
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="FXstreet read articlebidy error", code=6)



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

                    if child.tag == 'enclosure':
                        news['link'] = child.attrib['url']
                    news[child.tag] = child.text
                querry = {'link': news['link']}

                exist = checkForExist1(querry)
                if not exist:

                    desc = getArticleBody(news['link'], 'articlebody.html')
                    for c in desc:
                        news[c] = desc[c]
                    news = JsonItemStandard(news,classifier)
                    saveInMongo1(news)
                newsitems.append(news)

                # return news items list
        return newsitems
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="Investing XML reading Errorr", code=6)


def JsonItemStandard(newsItem,classifier):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider
    try:
        goldCommoditiesOptions = ['gold', 'xauusd']
        oilCommoditiesOptions = ['oil', 'brent', 'wti']
        silverCommoditiesOptions = ['silver', 'xagusd']
        copperCommoditiesOptions = ['copper']
        gasCommoditiesOptions = ['gas']
        item = {}
        # print(item)
        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['articleBody']
        currentDate = datetime.strptime(newsItem['pubDate'], '%b %d, %Y %H:%M GMT')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        item['pubDate'] = int(currentDate.timestamp())

        item['author'] = newsItem['author']
        item['link'] = newsItem['link']
        item['provider'] = 'Investing'
        item['category'] = 'Commodities'
        item['summary'] = ''
        item['thImage'] = ''
        #  Manual keywords initialization
        item['keywords'] = ''
        sw = 0
        for val in goldCommoditiesOptions:
            if val in newsItem['title'].lower().split():
                item['keywords'] = goldCommoditiesOptions
                sw = 1
                break
        if not sw:
            for val in oilCommoditiesOptions:
                if val in newsItem['title'].lower().split():
                    item['keywords'] = oilCommoditiesOptions
                    break
        if not sw:

            for val in silverCommoditiesOptions:
                if val in newsItem['title'].lower().split():
                    item['keywords'] = silverCommoditiesOptions
                    sw = 1
                    break
        if not sw:
            for val in copperCommoditiesOptions:
                if val in newsItem['title'].lower().split():
                    item['keywords'] = copperCommoditiesOptions
                    sw = 1
                    break
        if not sw:
            for val in gasCommoditiesOptions:
                if val in newsItem['title'].lower().split():
                    item['keywords'] = str(gasCommoditiesOptions).lstrip('[').rstrip(']')
                    sw = 1
                    break
        item['images'] = newsItem['images']
        results = classifier(item['title'])
        for result in results:
            item['Negative'] = result[0]['score']
            item['neutral'] = result[1]['score']
            item['Positive'] = result[2]['score']
        return item
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message, code=er.code)
    except:
        raise errors.DataProvidingException(message="Investing standardization error", code=6)




def getImageURL(content):
    try:

        soup = BeautifulSoup(content, 'html.parser')
        img_tags = soup.find_all('img', src=True)

        urls = [img['src'] for img in img_tags]
        return urls
    except :
        return ''



def checkForExist1(query):
    try:

        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        return resp['data']
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=6)
    except:
        raise errors.DataProvidingException(message="Investing: Error in saving to mongoengine", code=6)



def saveInMongo1(item):
    try:
        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.post(url, json=item)
        print(resp.text)
        # todo : exception handling
        return
    except requests.exceptions.ConnectionError as er:
        raise errors.DataProvidingException(message=er, code=6)
    except:
        raise errors.DataProvidingException(message="Failed to save in Mongoengine", code=6)


def investingFundamentalScraper(classifier):
    try:
        f = open('Forexlog.txt', 'a')
        url = 'https://www.investing.com/rss/commodities_Fundamental.rss'
        filename = 'topnewsfeed.xml'
        # load RSS File From Url
        now = datetime.now()
        print('crawling of Investing for Forex Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S ') + '(local time)!!')
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
        print("Error : Irregular Error from source number {code} ".format(code=6))



def main():

    #exportForexCSV ()
    investingFundamentalScraper()
    return
if __name__ == "__main__":

    # calling mpai2n function
    main()
