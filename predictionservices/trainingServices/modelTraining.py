import logging
import pathlib
from datetime import datetime

import numpy as np
import errors
from matplotlib import pyplot as plt
from dataProvidingServices.dataProviding import load_training_data
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Input, Dropout, LSTM
from tensorflow.keras.losses import MeanAbsolutePercentageError
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

Training = True


def create_model(input_shape: int) -> Model:
    lstm_shape = 128
    dropout = 0.2

    _input = Input(shape=input_shape)
    x2 = LSTM(lstm_shape, name="MarketRNN1", return_sequences=True)(_input)
    x2 = LSTM(lstm_shape, name="MarketRNN2")(x2)
    x2 = Dropout(dropout)(x2)
    x2 = Dense(1)(x2)

    return Model(input, x2)


def train_model(category, pair, news_keywords,
                provider=['fxstreet'],
                resolution=60,
                sequence_length=7, epochs=60, learning_rate=0.001, decay=1e-6, batch_size=32, validation_split=0.2, training=False):
    logging.info(
        f'-------------Start Model Training for currency pair {pair} with news keywords {news_keywords}--------------------------'
    )
    end_date = int(datetime.utcnow().timestamp())
    three_years_ts = 94867200
    two_years_ts = 63072000
    start_date = end_date - two_years_ts
    X_train, y_train, dates = load_training_data(category,
                                                 pair, start_date, end_date,
                                                 news_keywords,
                                                 resolution=resolution,
                                                 sequence_length=sequence_length,
                                                 training=training)

    # trade data RNN
    input_shape = (X_train.shape[1:])

    # Model
    market_model = create_model(input_shape)

    optimizer = Adam(lr=learning_rate, decay=decay)
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=30, min_delta=0.00001),
    ]

    market_model.compile(
        loss=MeanAbsolutePercentageError(),
        optimizer=optimizer)
    market_model.summary()

    history = market_model.fit(
        X_train, np.array(y_train),
        batch_size=batch_size,
        epochs=epochs,
        validation_split=validation_split,
        callbacks=callbacks
    )

    market_model.compile(
        loss=MeanAbsolutePercentageError(),
        optimizer=optimizer

    )

    market_model.summary()

    logging.info("plotting loss...")
    # plot loss
    plot_loss(history)
    plt.show()

    logging.info("successfully plotted loss...")

    # save model
    modelName = pair.upper() + 'WithNewsHourly.h5'
    current_Path = pathlib.Path().absolute()
    filePath = str(current_Path) + '/outputFiles/' + category + '/' + pair + '/' + modelName

    logging.info(f"saving trained model to {filePath}")
    market_model.save(filePath)

    logging.info('-------------successfully completed!--------------------------')


def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    # plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('Loss [Close]')
    plt.legend()
    plt.grid(True)


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    train_model(
        category='Forex',
        pair='EURUSD',
        news_keywords='EURUSD',
        provider=['fxstreet'],
        resolution=60,
        sequence_length=7, epochs=1, learning_rate=0.001, decay=1e-6, batch_size=32
    )


if __name__ == "__main__":
    main()