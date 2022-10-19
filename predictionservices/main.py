from ConceptModeling.conceptModeling import prepaireConcepts
from trainingServices.modelTraining import train_model
from predictionServices.predictCurrencyPair import predict_model
import schedule
import time
from datetime import datetime
import pandas as pd


def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))


def firstUsage():
    support = {
        'Forex': ['EURUSD', 'USDJPY', "GBPUSD", 'XAUUSD'],
        'CryptoCurrency': ['BTCUSDT'],
    }
    try:

        # ____________Model Training____________________ #
        train_model(category='Forex', pair='USDJPY', news_keywords='USDJPY',
                    provider=['fxstreet'], sequence_length=7,
                    epochs=150, learning_rate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='EURUSD', news_keywords='EURUSD',
                    provider=['fxstreet'], sequence_length=7,
                    epochs=150, learning_rate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='GBPUSD', news_keywords='GBPUSD',
                    provider=['fxstreet'], sequence_length=7, epochs=150, learning_rate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Cryptocurrency', pair='BTCUSDT', news_keywords='bitcoin',
                    provider=['fxstreet'], sequence_length=7,
                    epochs=300, learning_rate=0.5, decay=1e-3, batch_size=32)

    except Exception as err:
        print(err)
        return False


def predictionBussinessDay():
    try:
        time.sleep(2)
        predict_model(category='Forex', pair='EURUSD', newsKeywords='EURUSD',
                      provider=['fxstreet'],
                      resolution=60, SEQ_LEN=7,
                      )
        time.sleep(2)
        predict_model(category='Forex', pair='USDJPY', newsKeywords='USDJPY',
                      provider=['fxstreet'],
                      resolution=60, SEQ_LEN=7, )
        time.sleep(2)
        predict_model(category='Forex', pair='GBPUSD', newsKeywords='GBPUSD',
                      provider=['fxstreet'], resolution=60, SEQ_LEN=7)
        time.sleep(2)
        predict_model(category='Forex', pair='USDCHF', newsKeywords='USDCHF',
                      provider=['fxstreet'],
                      resolution=60, SEQ_LEN=7)
        time.sleep(2)

        predict_model(category='Forex', pair='XAUUSD', newsKeywords='gold',
                      provider=['fxstreet'],
                      resolution=60, SEQ_LEN=7)
        return True
    except Exception as err:
        print(str(err))
        return False


def predictionFullTimeMarket():
    try:
        time.sleep(2)
        predict_model(category='CryptoCurrency', pair='BTCUSDT', newsKeywords='bitcoin',
                      provider=['fxstreet'],
                      resolution=60, SEQ_LEN=7)


    except Exception as err:
        print(str(err))
        return False


def predictionServices():
    try:
        utcNow = datetime.utcnow()
        if is_business_day(utcNow):
            predictionBussinessDay()
        predictionFullTimeMarket()
    except Exception as err:
        print(str(err))
        return False


def trainingBussinessDay():
    try:
        train_model(category='Forex', pair='EURUSD',
                    news_keywords='EURUSD',
                    provider=['fxstreet'],
                    resolution=60,
                    sequence_length=7, epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='USDJPY',
                    news_keywords='USDJPY',
                    provider=['fxstreet'],
                    resolution=60,
                    sequence_length=7
                    , epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='GBPUSD',
                    news_keywords='GBPUSD',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60,
                    sequence_length=7, epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='USDCHF',
                    news_keywords='USDCHF',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60,
                    sequence_length=7
                    , epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='XAUUSD',
                    news_keywords='gold',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60,
                    sequence_length=7, epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )

    except Exception as err:
        print(str(err))
        return False


def trainingFullTimeMarkets():
    try:
        train_model(category='CryptoCurrency', pair='BTCUSDT',
                    news_keywords='bitcoin',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    sequence_length=7, max_L=15, conceptsType='pair'
                    , epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32
                    )
    except Exception as err:
        print(str(err))
        return False


def trainingServices():
    try:
        utcNow = datetime.utcnow()
        if is_business_day(utcNow):
            trainingBussinessDay()
        trainingFullTimeMarkets()
    except Exception as err:
        print(str(err))
        return False



def start():
    print('started!!')
    print('+---------------------------------------------+')
    schedule.clear()

    schedule.every(24).hours.do(trainingServices)

    schedule.every(1).minutes.do(predictionServices)

    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    # firstUsage()
    start()


if __name__ == "__main__":
    # calling mpai2n function
    main()