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

import tensorflow as tf
# Import libraries
import json
import numpy as np
import csv
import re
import time
from sklearn import metrics
from datetime import datetime
from datetime import timedelta
import tensorflow as tf
from tensorflow import keras
from flask import Flask, render_template, request

application = Flask(__name__, template_folder='templates')

# Load data coordinates for NYC airports
JFK = open('JFK2.txt', 'r')
LAGUARDIA = open('LaGuardia2.txt', 'r')
NEWARK = open('Newark2.txt', 'r')
manhattan_ = open('Manhattan.txt', 'r')

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

global model,manhattan,air_ports
jfk_coords = (40.639722, -73.778889)
lga_coords = (40.77725, -73.872611)
nwk_coords = (40.6925, -74.168611)

@application.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@application.route('/getFare',methods=['POST'])
def map():
    if request.method == 'POST':
        data = request.get_json()

        pickup_latitude = float(data['pickup_latitude'])
        pickup_longitude = float(data['pickup_longitude'])
        dropoff_latitude = float(data['dropoff_latitude'])
        dropoff_longitude = float(data['dropoff_longitude'])
        passenger_count = float(data['passengers'])
        year = float(data['year'])
        month = float(data['month'])
        weekday = float(data['day'])
        hour = float(data['hour'])
        minute = float(data['minute'])
        weekend = 0.0 if weekday == 1.0 else 1.0


        original_query = [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude, passenger_count, year, month, weekday, weekend, hour, minute]
        print("check 1:",original_query)
        # original_query = [-74.004277, -74.001712, 40.74272, 40.751197, 5.0, 2009, 6, 0, 0, 17, 26]
        all_queries,before_expanding = get_all_converted_queries(original_query)

        print("check 2")

        return_predictions = getPredictions(all_queries, original_query,before_expanding)
        print("check 4")

        ret = []
        resp = {}
        for pred in return_predictions:
            resp = {
            'distance_to_new_point':pred['distance_to_new_point'],
                       'pickup_latitude': pred['pickup_latitude'],
                       'pickup_longitude': pred['pickup_longitude'],
                       'dropoff_latitude':pred['dropoff_latitude'],
                       'dropoff_longitude': pred['dropoff_longitude'],
                       'distance_km': pred['distance_km'],
                       'fare': round(pred['fare'],2),
                        'direction': pred['direction'],
                        'hour':pred['hour'],
                        'minute':pred['minute']
                       }
            ret.append(resp)


         # distance_to_new pickup_point, plat, plong, dlat, dlong, distance_km, fare
    print(type(resp))
    returnJSON = json.dumps(ret, cls=NumpyEncoder)
    print("json",returnJSON)

    return returnJSON

def getPredictions(all_queries, original_query,before_expanding):
    predictions = model.predict(all_queries)
    print("check 3")

    lat,lon = original_query[2],original_query[0]
#     only sending back required columns
    final_queries = []
    acutal_fare = predictions[0][0]
    for i,pred in enumerate(predictions):
        [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude,
         passenger_count, year, weekday, weekend, hour_sin,
         month_sin, delta_longitude, delta_latitude, distance_km, direction, dropoff_manhattan, pickup_manhattan,
         peak_hours,
         JFK, LGA, NWK] = all_queries[i]

        distance_to_new_point = haversine(lat,lon,pickup_latitude,pickup_longitude)



        final_query = {
            'distance_to_new_point':distance_to_new_point,
                       'pickup_latitude': pickup_latitude,
                       'pickup_longitude': pickup_longitude,
                       'dropoff_latitude':dropoff_latitude,
                       'dropoff_longitude': dropoff_longitude,
                       'distance_km': distance_km,
                       'fare': round(pred[0],2),
                        'direction': direction,
                        'hour':before_expanding[i][9],
                        'minute':before_expanding[i][10]
                       }

        if round(acutal_fare,1) >= round(pred[0],1):
            # print("FQ:", final_query)
            final_queries.append(final_query)
        else:
            print("Discared",final_query['fare'], "-",round(acutal_fare,2))
    return final_queries


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


def define_all_air_ports(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude):
    # nonlocal air_ports
    JFK = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, air_ports[0])
    LGA = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, air_ports[1])
    NWK = in_airport(dropoff_latitude, dropoff_longitude, pickup_latitude, pickup_longitude, air_ports[2])
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

def getNearQueries(main_query):
    print(main_query)
    [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude, passenger_count, year,
                      month, weekday, weekend, hour, minute] = main_query
    other_queries = []

    # changing pickup_longitude
    q1 = main_query[:]
    plong = pickup_longitude - 0.005
    q1[0] = plong
    # changing pickup_latitude
    q2 = main_query[:]
    plat = pickup_latitude - 0.005
    q2[2] = plat

    other_queries.append(q1)
    other_queries.append(q2)

    # changing pickup_longitude
    q3 = main_query[:]
    plong = pickup_longitude + 0.01
    q3[0] = plong
    # changing pickup_latitude
    q4 = main_query[:]
    plat = pickup_latitude + 0.01
    q4[2] = plat

    # # changing dropoff_longitude
    # q3 = main_query[:]
    # dlong = dropoff_longitude + 0.001
    # q3[1] = dlong
    # # changing dropoff_latitude
    # q4 = main_query[:]
    # dlat = dropoff_latitude + 0.001
    # q4[3] = dlat

    other_queries.append(q3)
    other_queries.append(q4)
    # other_queries.append(q3)
    # other_queries.append(q4)

    # time features - hour, minute
    time = datetime.strptime(str(int(hour))+":"+str(int(minute)), '%H:%M')
    new_time_1 = time + timedelta(minutes=5)
    new_time_2 = time + timedelta(minutes=10)
    new_time_3 = time + timedelta(minutes=15)
    hour1,minute1 = float(new_time_1.strftime('%H')),float(new_time_1.strftime('%M'))
    hour2,minute2 = float(new_time_2.strftime('%H')),float(new_time_2.strftime('%M'))
    hour3,minute3 = float(new_time_3.strftime('%H')),float(new_time_3.strftime('%M'))
    q5 = main_query[:]

    q5[9],q5[10] = hour1,minute1

    q6 = main_query[:]
    q6[9],q6[10] = hour2,minute2

    q7 = main_query[:]
    q7[9],q7[10] = hour3,minute3


    other_queries.append(q5)
    other_queries.append(q6)
    other_queries.append(q7)

    # mix max
    q11,q12,q13,q14 = q1[:],q2[:],q3[:],q4[:]
    q11[9], q11[10] = hour1,minute1
    q12[9], q12[10] = hour1,minute1
    q13[9], q13[10] = hour1,minute1
    q14[9], q14[10] = hour1,minute1
    other_queries.append(q11)
    other_queries.append(q12)
    other_queries.append(q13)
    other_queries.append(q14)

    q21, q22, q23, q24 = q1[:], q2[:], q3[:], q4[:]
    q21[9], q21[10] = hour2, minute2
    q22[9], q22[10] = hour2, minute2
    q23[9], q23[10] = hour2, minute2
    q24[9], q24[10] = hour2, minute2
    other_queries.append(q21)
    other_queries.append(q22)
    other_queries.append(q23)
    other_queries.append(q24)

    q31, q32, q33, q34 = q1[:], q2[:], q3[:], q4[:]
    q31[9], q31[10] = hour3, minute3
    q32[9], q32[10] = hour3, minute3
    q33[9], q33[10] = hour3, minute3
    q34[9], q34[10] = hour3, minute3

    other_queries.append(q31)
    other_queries.append(q32)
    other_queries.append(q33)
    other_queries.append(q34)
    return other_queries


def get_all_converted_queries(main_query):
    near_queries = getNearQueries(main_query)
    before_expanding = [main_query] + near_queries
    all_queries = []
    for query in before_expanding:
        all_queries.append(get_queries(query))
    return all_queries,before_expanding

def get_queries(main_query):
    [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude,passenger_count, year, month, weekday, weekend, hour, minute] = main_query

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
    dropoff_manhattan = in_manhattan(manhattan, dropoff_latitude, dropoff_longitude)
    pickup_manhattan = in_manhattan(manhattan, pickup_latitude, pickup_longitude)

    # Find how many fares begin/end at an airport
    JFK, LGA, NWK = define_all_air_ports(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)

    main_query = [pickup_longitude, dropoff_longitude, pickup_latitude, dropoff_latitude,
     passenger_count, year, weekday, weekend, hour_sin,
                  month_sin, delta_longitude, delta_latitude, distance_km, direction, dropoff_manhattan, pickup_manhattan, peak_hours,
                  JFK, LGA, NWK]


    return main_query

def init_manhattan():
    for line in manhattan_:
        line = line.split(',')
        polygon_y = [np.float64(i) for i in line[::2]]
        polygon_x = [np.float64(i) for i in line[1::2]]
        manhattan = (merge(polygon_x, polygon_y))
    manhattan_.close()
    return manhattan

def init_airports():
    airports = []

    for airport in [JFK, LAGUARDIA, NEWARK]:
        for line in airport:
            line = line.split(',')
            polygon_y = [np.float64(i) for i in line[::2]]
            polygon_x = [np.float64(i) for i in line[1::2]]
            airports.append(merge(polygon_x, polygon_y))
    return airports

def initApp():
    global model,manhattan,air_ports
    model = tf.keras.models.load_model('new_model')
    # Load data coordinates for Manhattan
    manhattan = init_manhattan()
    air_ports = init_airports()


if __name__ == '__main__':

    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    initApp()
    application.run("127.0.0.1",port=5000)
