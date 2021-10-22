## Scheduler module that schedule following services:

- News Scraping services that fetch news from specialized financial newsgroupes and POST data to our Mongo engine Services.
- Data providing services including Market information (from [finnhub API](https://finnhub.io/)) and news from our Mongo engine services. 
- Model training services that fetch data from our data providing services and work on Tensorflow 2. 
- Prediction Services that predict particular currency pairs and work on Tensorflow2.

### Data providing services
For checking our news data providing services, please refer to dataProvidingServices folder.

<hr/>

### Model training services
This services currently available for four currency pairs of [ EUR_USD , USD_JPY , GBP_USD , BTC_USDT] based on resolution 60 minutes.
With these services we schedule our predictive model training every month. The implementation of our predictive model is based on **FinBERT** text representation and Recurrent neural network which implemented in **KERAS functional API**.
We train our predictive modeles based on **over 2 years** of our news data .
For checking our news data providing services, please refer to TrainingServices folder.

<hr/>

### Prediction services
This services currently available for two categories of Forex and cryptocurrency markets and also four currency pairs of [ EUR_USD , USD_JPY , GBP_USD, XAU_USD, USD_CHF  , BTC_USDT] based on resolution 60 minutes.
We schedule our prediction services every hours in business days and POST the predicted values to our Mongo engine services.
For checking our prediction services, please refer to predictionServices folder.

#### for running this service :

pip install

python run main.py

