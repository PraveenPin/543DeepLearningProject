# Import libraries
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from shapely.geometry.polygon import Polygon,Point

from sklearn.svm import SVR
from sklearn.ensemble import BaggingRegressor
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import VotingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingRegressor

import keras
from keras.datasets import mnist
from keras.initializers import TruncatedNormal
from keras.layers import Conv2D, Dense, Flatten, Input, MaxPooling2D
from keras.models import Model, Sequential
# from keras.optimizers import Adam
import keras.backend as K
import keras.optimizers as opt
# Import libraries
import numpy as np
import csv
import re
import time
from sklearn import metrics
import tensorflow as tf
from tensorflow import keras

# Load data coordinates for NYC airports
JFK = open('JFK2.txt','r')
LAGUARDIA = open('LaGuardia2.txt','r')
NEWARK = open('Newark2.txt','r')
manhattan_ = open('Manhattan.txt','r')

jfk_coords = (40.639722, -73.778889)
lga_coords = (40.77725, -73.872611)
nwk_coords = (40.6925, -74.168611)

# Load data coordinates for Manhattan
def init_manhattan():
    for line in manhattan_:  
      line = line.split(',')   
      polygon_y = [ np.float64(i) for i in line[::2] ]  
      polygon_x = [ np.float64(i) for i in line[1::2] ]   
      manhattan = (merge(polygon_x, polygon_y))
    manhattan_.close()
    return manhattan

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def get_direction(lat1, lon1, lat2, lon2):
  diff_lon = np.deg2rad(lon2-lon1)
  x = np.sin(diff_lon) * np.cos(lat2)
  y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(diff_lon))
  initial_bearing = np.arctan2(x, y)

  direction = np.degrees (initial_bearing)

  initial_bearing = np.degrees (initial_bearing)
  direction = (initial_bearing + 360) % 360
  return direction


def haversine(lat1, lon1, lat2, lon2):
  # convert decimal degrees to radians
  lon1=np.deg2rad(lon1)
  lat1=np.deg2rad(lat1)
  lon2=np.deg2rad(lon2)
  lat2=np.deg2rad(lat2)
  # haversine formula
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
  c = 2 * np.arcsin(np.sqrt(a))
  r = 6372.8 # Radius of earth in kilometers. Use 3956 for miles
  return np.around(c * r, decimals=2)

# Function for fares from/to Manhattan
def in_manhattan(manhattan, x, y):   
  point = Point(float(x), float(y))  
  found = 0
  polygon = Polygon(manhattan) 
  if polygon.contains(point) == 1:
    found = 1   
    return found
  return found

# Load file with polygon coordinates
def merge(list1, list2):
  merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
  return merged_list

# Function to find points pick_up at airports
def in_airport(x1,y1,x2,y2,airport):
  for icoord, (x,y) in enumerate(zip([x1,x2], [y1,y2])):
    point = Point(float(x), float(y))
    found = 0
    polygon = Polygon(airport)
    if polygon.contains(point) == True:
      found = 1
      return found
  return found


def init_airports():
    airports = []

    for airport in [JFK, LAGUARDIA, NEWARK]:
        for line in airport:
            line = line.split(',')
            polygon_y = [np.float64(i) for i in line[::2]]
            polygon_x = [np.float64(i) for i in line[1::2]]
            airports.append(merge(polygon_x, polygon_y))
    return airports

def define_all_air_ports(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude):
    airports = init_airports()
    JFK = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, airports[0])
    LGA = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, airports[1])
    NWK = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, airports[2])
    return JFK,LGA,NWK

# Function for fares from/to Manhattan
def in_manhattan(manhattan, x, y):
  point = Point(float(x), float(y))
  found = 0
  polygon = Polygon(manhattan)
  if polygon.contains(point) == 1:
    found = 1
    return found
  return found

def get_queries(main_query):

    [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude,
     passenger_count, year, month, weekday, weekend, hour, minute] = main_query
    month_sin = np.sin((month - 1) * (2. * np.pi / 12))
    weekday_sin = np.sin((weekday - 1) * (2. * np.pi / 7))
    hour_sin = np.sin((hour + minute / 60) * (2. * np.pi / 24))
    distance_km = haversine(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)
    direction = get_direction(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)

    # abs of delta of longitude and latitude pickup-dropoff
    delta_longitude = abs(pickup_longitude - dropoff_longitude)
    delta_latitude = abs(pickup_latitude - dropoff_latitude)
    # peak_hours
    peak_hours = 1 if hour in [18, 19, 20] else 0

    # Find how many fares begin/end at Manhattan
    manhattan = init_manhattan()
    dropoff_manhattan = in_manhattan(manhattan, dropoff_latitude, dropoff_longitude)
    pickup_manhattan = in_manhattan(manhattan, pickup_latitude, pickup_longitude)

    # Find how many fares begin/end at an airport
    JFK, LGA, NWK = define_all_air_ports(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)

    main_query = [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude,
     passenger_count, year, weekday, weekend, hour_sin,
                  month_sin, delta_longitude, delta_latitude, distance_km, direction, dropoff_manhattan, pickup_manhattan, peak_hours,
                  JFK, LGA, NWK]

    all_queries = [main_query]
    return all_queries

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(tf.version.VERSION)

    # The patience parameter is the amount of epochs to check for improvement
    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)


    columns = ['pickup_longitude','dropoff_longitude','pickup_latitude',
                  'dropoff_latitude','passenger_count','year','weekday','weekend','hour_sin','month_sin',
                  'delta_longitude','delta_latitude','distance_km','direction',
                  'dropoff_manhattan','pickup_manhattan','peak_hours','JFK','LGA',
                  'NWK']

    # train model
    epochs = 20
    batch_size = 32

    start_time = time.time()

    model = tf.keras.models.load_model('saved_model/DNN_model_with_weights')


    pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude = -74.004277, -74.001712, 40.74272, 40.751197

    passenger_count = 1

    year, month, weekday, weekend, hour, minute = 2009, 6, 0, 0, 17,26

    original_query = [-74.004277, -74.001712, 40.74272, 40.751197, 5.0, 2009, 6, 0, 0, 17,26]
    all_queries = get_queries(original_query)


    print("all queries",all_queries)

    predictions = model.predict(all_queries)

    print('PyCharm',predictions)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
