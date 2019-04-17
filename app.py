#!/usr/local/bin/python
from flask import Flask, abort, request, render_template, redirect
import csv
import json
import ast
from flask_api import status
import pandas as pd
import numpy as np
from sklearn import datasets, linear_model
from datetime import datetime, timedelta
from collections import OrderedDict
from tempfile import NamedTemporaryFile
from flask_api import status
# from flask_restful import Resource, Api
from flask_restplus import Api, Resource, fields
import math
import random

app = Flask(__name__)
api = Api(app, version='1.0', title="Weather API")

@app.route('/weather/',methods=['GET'])
def Historical():
    return render_template('index.html')


@app.route('/historical/',methods=['GET'])
def index():
    with open('dailyweather.csv', 'r') as f:
        row_count = sum(1 for row in f)
        f = open('dailyweather.csv', 'r')
        reader = csv.reader(f)
        next(reader)

        dumper_list = []

        for row in range(1,row_count):
            dict_= {}
            value = next(reader)
            dict_["DATE"]= value[0]
            dumper_list.append(dict_)
            json_ = json.dumps(dumper_list, separators=[",", ":"])
    f.close()
    return json_

@app.route('/historical/<param>', methods=['GET'])
def weatherInfo(param):
    with open('dailyweather.csv', 'r') as f:
        row_count = sum(1 for row in f)
        f = open('dailyweather.csv', 'r')
        reader = csv.reader(f)
        next(reader)
        dumper_list = []
        trigger = 0

        for row in range(1,row_count):
            dict_= {}
            value = next(reader)

            if value[0] == param:
                
                # dict_= {}
                dict_= {"DATE": str(value[0]), "TMAX" : float(value[1]), "TMIN" : float(value[2])}
                json_ = json.dumps(dict_,sort_keys=True)
                trigger = 1
                break
    f.close()
    if trigger == 0:
        abort(404)
    else:
        return json_


@app.route('/historical/', methods=['POST'])
def post_info():
    print("in here")
    data = json.loads(str(request.data, encoding='utf-8'))
    # data = request.data
    date = data['DATE']
    tmax = float(data['TMAX'])
    tmin = float(data['TMIN'])
    file_ = open('dailyweather.csv', 'r')
    fieldnames = ("DATE", "TMAX","TMIN")
    reader = csv.DictReader(file_, fieldnames)
    dict_ = {}
    next(reader)
    for row in reader:
        dict_[row["DATE"]] = {row["TMAX"], row["TMIN"]}

    dict_[date] = tmax, tmin
    sorted_dict = OrderedDict(sorted(dict_.items()))
    with open('dailyweather.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["DATE","TMAX","TMIN"])
        for key, value in sorted_dict.items():
            a, b = value
            writer.writerow([key, a, b])
    file_.close()
    date_dict = {}
    date_dict = json.dumps({"DATE": date})
    return date_dict, status.HTTP_201_CREATED

@app.route('/historical/<info>', methods=['DELETE'])
def remove_info(info):
    date = ast.literal_eval(info)
    trigger = 0
    data_df = pd.read_csv('dailyweather.csv')
    for i in range(0,data_df.shape[0]):
        if data_df.DATE[i] == date:
            trigger = 1
            data_df.drop(i,inplace=True)
            data_df.to_csv('dailyweather.csv', index=False)
    if trigger == 1:
        dict_ = json.dumps({"DATE":date})
        return dict_, status.HTTP_200_OK
    else:
        dict_ = json.dumps({"DATE":date})
        return dict_, status.HTTP_204_NO_CONTENT

@app.route('/forecast/<param>', methods=["GET"])
def get(param):
    data_df = pd.read_csv('dailyweather.csv')
    date_train = data_df[data_df.columns[0]]
    date_train = np.array(date_train).reshape(-1,1)
    tmax_train = data_df[data_df.columns[1]]
    tmax_train = np.array(tmax_train).reshape(-1,1)
    tmin_train = data_df[data_df.columns[2]]
    tmin_train = np.array(tmin_train).reshape(-1,1)

    regr1 = linear_model.LinearRegression()
    regr1.fit(date_train, tmax_train)

    regr2 = linear_model.LinearRegression()
    regr2.fit(date_train, tmin_train)

    a = next_date(param)

    tmax_predict = regr1.predict(np.array(a).reshape(-1,1))
    tmin_predict = regr2.predict(np.array(a).reshape(-1,1))

    dumper_list = []

    for i in range(0,7):
        dict_= {}        
        if a[i] in data_df[data_df.columns[0]].values:
            values = data_df.loc[data_df['DATE'] == a[i]]
            dict_["DATE"]= values.iloc[0]['DATE']
            dict_["TMAX"]= values.iloc[0]['TMAX']
            dict_["TMIN"]= values.iloc[0]['TMIN'] 
            sorted_dict = OrderedDict(sorted(dict_.items()))   
        else:
            dict_["DATE"]= str(a[i])
            dict_["TMAX"]= round(tmax_predict[i][0],2) + random.uniform(3,5)
            dict_["TMIN"]= round(tmin_predict[i][0],2) + random.uniform(0,3)
            sorted_dict = OrderedDict(sorted(dict_.items()))
        dumper_list.append(sorted_dict)
        json_ = json.dumps(dumper_list)

    return json_

def next_date(this_date):
    date_ = datetime.strptime(this_date, '%Y%m%d')
    date_list = []
    date_list.append(int(this_date))
    for i in range(0,6):
            date_ += timedelta(days=1)
            d = int(date_.strftime('%Y%m%d'))
            date_list.append(d)
    return date_list

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
