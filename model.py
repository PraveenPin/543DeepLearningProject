# Import libraries
from sklearn.model_selection import train_test_split
from keras.layers import  Dense
from keras.models import Sequential

import pandas as pd

import tensorflow as tf

import os
from keras.layers import Dropout
import matplotlib.pyplot as plt


print(tf.version.VERSION)

INPUT_DATA_DIR = "../preprocessed_input/"
TRAIN_DATA_COEFFICIENT = 0.70


def tf_data_generator(file_list, batch_size=1):
    counter = 0

    while True:
        fname = file_list[counter]

        counter = (counter + 1) % len(file_list)
        df = pd.read_csv(INPUT_DATA_DIR + fname)
        df.dtypes

        df.drop(['pickup_datetime'], axis=1, errors='ignore')

        input = df[['pickup_longitude', 'dropoff_longitude', 'pickup_latitude',
                    'dropoff_latitude', 'passenger_count', 'year', 'weekday', 'weekend', 'hour_sin', 'month_sin',
                    'delta_longitude', 'delta_latitude', 'distance_km', 'direction',
                    'dropoff_manhattan', 'pickup_manhattan', 'peak_hours', 'JFK', 'LGA',
                    'NWK']].copy().astype(float)

        output = df['fare_amount'].copy()

        for local_index in range(0, input.shape[0], batch_size):
            input_local = input[local_index:(local_index + batch_size)]
            output_local = output[local_index:(local_index + batch_size)]
            print(output_local.shape)

            yield input_local, output_local


def build_model():
  model = Sequential()
  model.add(Dense(20, activation='relu', input_dim=20))
  model.add(Dropout(0.2))
  model.add(Dense(128, activation='relu'))
  model.add(Dropout(0.2))
  model.add(Dense(64, activation='relu'))
  model.add(Dropout(0.2))
  model.add(Dense(32, activation='relu'))
  model.add(Dropout(0.2))
  model.add(Dense(16, activation='relu'))
  model.add(Dense(1,  activation='relu'))

  model.compile(loss='mse', optimizer = 'adam', metrics=['mse','mae'])
  return model

if __name__ == '__main__':

    # to store all the input csv file names
    files = []
    for (dirpath, dirnames, filenames) in os.walk(INPUT_DATA_DIR):
        files.extend(filenames)
        break

    # splitting the whole data into 80% training data, and 20% testing data
    train_file_names, test_file_names = train_test_split(files, test_size=0.2, random_state=321)
    # splitting the 80% training data into 85% training_data and 15% validation data
    train_file_names, validation_file_names = train_test_split(train_file_names, test_size=0.15, random_state=232)

    print("Number of train_files:", len(train_file_names))
    print("Number of validation_files:", len(validation_file_names))
    print("Number of test_files:", len(test_file_names))

    # since each csv file contains approx 1M rows, and our batch size is 100000
    # => each file has to be called 10 times in each epoch to exhaust the data
    batch_size = 100000
    train_dataset = tf.data.Dataset.from_generator(
        generator=lambda: tf_data_generator(file_list=train_file_names, batch_size=batch_size),
        output_shapes=((None, 20), (None,)),
        output_types=(tf.float32, tf.float32))

    validation_dataset = tf.data.Dataset.from_generator(
        generator=lambda: tf_data_generator(file_list=validation_file_names, batch_size=batch_size),
        output_shapes=((None, 20), (None,)),
        output_types=(tf.float32, tf.float32))

    test_dataset = tf.data.Dataset.from_generator(
        generator=lambda: tf_data_generator(file_list=test_file_names, batch_size=batch_size),
        output_shapes=((None, 20), (None,)),
        output_types=(tf.float32, tf.float32))

    # create model
    model = build_model()
    model.summary()

    # since each file has to be called 10 times, and data in all training files has to be used
    # steps in each epoch => number_of_training_file * (total_row_in_csv_file / batch_size) =  370
    hist = model.fit(
        steps_per_epoch=len(train_file_names)*10,
        use_multiprocessing=True,
        workers=6,
        x=train_dataset,
        verbose=1,
        max_queue_size=32,
        epochs=50,
        #     callbacks=callback_list,
        validation_data=test_dataset,
        validation_steps=len(validation_file_names)*10
    )

    model.save('new_model')
    loss, mse, mae = model.evaluate(
    x=test_dataset, steps=len(test_file_names)*10,callbacks=None, max_queue_size=32, workers=6, use_multiprocessing=True,
    return_dict=False)

    plt.figure(figsize=(20,10))
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train','test'],loc='upper right')
    plt.show()
