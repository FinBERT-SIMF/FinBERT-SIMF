from datetime import datetime
from predictionservices.dataProvidingServices.dataProviding import prepairDataForLoad
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Dense, Input, Dropout, LSTM, Conv1D, MaxPooling1D
from tensorflow.keras.regularizers import l2
from matplotlib import pyplot as plt
import predictionservices. errors
import pathlib
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.losses import MeanAbsolutePercentageError

Training = True

def train_model(category, pair, newsKeywords,
                provider=['fxstreet'],
                resolution=60,
                SEQ_LEN=7 , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32):
    try:
        print('-------------Start Model Training for currency pair {a} with news keywords {b}--------------------------'.format(a = pair,b=newsKeywords))
        endDate =int( datetime.utcnow().timestamp())
        threeYearsTS = 94867200
        twoYearsTS = 63072000
        startDate = endDate - twoYearsTS
        train_x, train_y, dates = prepairDataForLoad(category,
                                                                   pair, startDate, endDate,
                                                                   newsKeywords, provider=provider,
                                                                    resolution=resolution,
                                                                   SEQ_LEN=SEQ_LEN,
                                                                    Training=True)

        # trade data RNN
        input_shape = (train_x.shape[1:])
        input = Input(shape=input_shape)
        x2 = LSTM(128, name="MarketRNN1", return_sequences=True)(input)
        x2 = LSTM(128,name="MarketRNN2") (x2)
        x2 = Dropout(0.2)(x2)
        x2 = Dense(1)(x2)
        marketModel = Model(input, x2)

        opt = tf.keras.optimizers.Adam(lr=learningRate, decay=decay)
        callback = EarlyStopping(monitor='val_loss', patience=30, min_delta=0.00001, )

        marketModel.compile(
            loss=MeanAbsolutePercentageError(),
            optimizer=opt)
        marketModel.summary()

        history = marketModel.fit(
            train_x, np.array(train_y),
            batch_size=batch_size,
            epochs=epoch,
            validation_split=0.2,
            callbacks=[callback])

        marketModel.compile(
            loss=tf.keras.losses.MeanAbsolutePercentageError(),
            optimizer=opt

        )

        marketModel.summary()

        plot_loss(history)
        plt.show()
        modelName = pair.upper() + 'WithNewsHourly.h5'
        current_Path = pathlib.Path().absolute()
        filePath = str(current_Path)+'/outputFiles/' + category + '/' + pair + '/' + modelName
        marketModel.save(filePath)
        print('-------------successfully completed!--------------------------')
    except predictionservices.errors.DataProvidingException as err:
        print(err.message)
        return False
    except:
        print("Something Went Wrong!")
        return False



def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    # plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('Loss [Close]')
    plt.legend()
    plt.grid(True)


def main():

    train_model(category='Forex', pair='USDJPY', newsKeywords='USDJPY',
                provider=['fxstreet'],
                resolution=60,  SEQ_LEN=7,
                epoch=150,learningRate=0.001,decay=1e-6,batch_size=32)
    return


if __name__ == "__main__":
    main()
