import datetime
from functools import wraps
from flask import Flask, jsonify, render_template
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app)
app.config.from_pyfile('config.py')


def get_access_token():
    token_url = app.config['TOKEN_URL']
    auth = HTTPBasicAuth(app.config['CLIENT_ID'], app.config['SECRET_ID'])
    response = requests.post(token_url, auth=auth)
    data = response.json()
    access_token = data.get('access_token')
    return access_token


def provide_access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = get_access_token()
        kwargs['access_token'] = access_token
        return func(*args, **kwargs)

    return wrapper


@provide_access_token
def get_actual_generations_per_unit(start_date, end_date, access_token):
    url = app.config['ACTUAL_GENERATION_PER_UNIT_URL']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    start_datetime = datetime.datetime.fromisoformat(start_date)
    end_datetime = datetime.datetime.fromisoformat(end_date)
    duration = end_datetime - start_datetime

    if duration.days > 7:
        result = []

        interval_start = start_datetime

        while interval_start < end_datetime:
            interval_end = interval_start + datetime.timedelta(days=7)
            interval_end = min(interval_end, end_datetime)

            if (interval_end - interval_start).days < 7:
                interval_end = interval_end + datetime.timedelta(days=1)

            params = {
                'start_date': interval_start.isoformat(),
                'end_date': interval_end.isoformat(),
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json().get('actual_generations_per_unit', [])

            result.extend(data)

            if (interval_end - interval_start).days < 7:
                break

            interval_start = interval_end - datetime.timedelta(days=1)

        return {'actual_generations_per_unit': result}

    else:
        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json().get('actual_generations_per_unit', [])

        return {'actual_generations_per_unit': data}


@app.route('/data')
def get_data():
    start_date = '2022-12-01T00:00:00+02:00'
    end_date = '2022-12-11T00:00:00+02:00'
    data = get_actual_generations_per_unit(start_date, end_date)
    return jsonify(data)


def transform_data(data):
    df = pd.DataFrame(data)
    # Assuming your DataFrame is named 'df'
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # Extract the relevant columns from the 'unit' column
    df["unit_eic_code"] = df["unit"].apply(lambda x: x["eic_code"])
    df["unit_name"] = df["unit"].apply(lambda x: x["name"])
    df["unit_production_type"] = df["unit"].apply(lambda x: x["production_type"])
    # Drop rows where production_type is not NUCLEAR
    df = df[df['unit_production_type'] == 'NUCLEAR']

    # Drop the unnecessary columns
    df.drop(columns=["unit"], inplace=True)
    # Explode the 'values' column to create separate rows for each value
    df = df.explode("values")
    # Extract the necessary columns from 'values' and convert datetime strings to datetime objects
    df["value_start_date"] = pd.to_datetime(df["values"].apply(lambda x: x["start_date"]))
    df["value_end_date"] = pd.to_datetime(df["values"].apply(lambda x: x["end_date"]))
    df["value_updated_date"] = pd.to_datetime(df["values"].apply(lambda x: x["updated_date"]))
    df["value"] = df["values"].apply(lambda x: x["value"])

    # Drop the unnecessary column
    df.drop(columns=["values"], inplace=True)
    return df


def production_average_per_hour(data):
    df = transform_data(data)

    # Extract the hour from 'start_date' column and create a new column 'hour'
    df['hour'] = df['value_start_date'].dt.hour

    # Une valeur par intervalle de temps, regles: AGPU-RG07 AGPU-RG07: Il n’y a pas de gestion de changement d’heure.
    # Le Service retourne tout le temps 24 valeurs, une valeur par heure. Group by 'hour' and calculate the average
    # value
    df_hourly_avg = df.groupby('hour')['value'].mean()

    # Store the average values in a dictionary
    hourly_avg_dict = {}
    for hour, avg_value in df_hourly_avg.items():
        hourly_avg_dict[f"Hour {hour}"] = avg_value

    return hourly_avg_dict


def production_sum_per_hour_of_day(data):
    df = transform_data(data)

    # Extract the hour from 'start_date' column and create a new column 'hour'
    df['hour'] = df['value_start_date'].dt.hour

    # Group by 'day' and 'hour' and calculate the sum of values
    df_hourly_sum = df.groupby([df['value_start_date'].dt.date, df['hour']])['value'].sum()

    # Store the sum of values in a dictionary
    hourly_sum_dict = {}

    for (day, hour), sum_value in df_hourly_sum.items():
        day_str = day.strftime("%Y-%m-%d")  # Format day as a string
        if day_str not in hourly_sum_dict:
            hourly_sum_dict[day_str] = {}
        hourly_sum_dict[day_str][f"Hour {hour}"] = sum_value
    return hourly_sum_dict


@app.route('/')
def index():
    start_date = '2022-12-01T00:00:00+02:00'
    end_date = '2022-12-11T00:00:00+02:00'

    data = get_actual_generations_per_unit(start_date, end_date)
    data = data.get('actual_generations_per_unit')

    production_sum_per_hour_of_day_data = production_sum_per_hour_of_day(data)
    production_average_per_hour_data = production_average_per_hour(data)

    return render_template('index.html',
                           average_data=production_average_per_hour_data, sum_data=production_sum_per_hour_of_day_data)


if __name__ == '__main__':
    app.run()
