import sys,time
from datetime import datetime
import schedule
from newsScraper.FxstreetScraper import fxstreetScraper
from newsScraper.FxstreetBitcoinScraper import fxstreetBitcoinScraper
from newsScraper.BitcoinNewsScraper import     bitcoinNewsScrapper
from newsScraper.cointelegraphScanner import cointelegraphScraper
from newsScraper.InvestingCommoditiesTechnicalScraper import investingTechnicalScraper
from newsScraper.InvestingCommoditiesFundameentalScraper import investingFundamentalScraper
from newsScraper.ForexNewsAPI import ForexNewsApi
from newsScraper.BitcoinNewsAPI import bitcoinNewsApi
from transformers import AutoTokenizer, AutoModelForSequenceClassification,pipeline

sys.setrecursionlimit(1000)


def startMostPublished (classifier):

    fxstreetScraper(classifier)
    fxstreetBitcoinScraper(classifier)
    bitcoinNewsScrapper(classifier)
    cointelegraphScraper(classifier)
    investingTechnicalScraper(classifier)
    investingFundamentalScraper(classifier)

def longTimeStart(classifier):
    bitcoinNewsApi(classifier)
    ForexNewsApi(classifier)


def start():
    tokenizer = AutoTokenizer.from_pretrained("ipuneetrathore/bert-base-cased-finetuned-finBERT")
    model = AutoModelForSequenceClassification.from_pretrained("ipuneetrathore/bert-base-cased-finetuned-finBERT")
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, )
    classifier.return_all_scores = True
    schedule.every(20).minutes.do( startMostPublished,classifier )

    schedule.every(600).minutes.do( longTimeStart,classifier )




    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    start()
if __name__ == '__main__':
    start()

