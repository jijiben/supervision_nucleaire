import datetime
from functools import wraps
from flask import Flask, jsonify, render_template
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from flask_caching import Cache

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Configure and initialize the cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

TOKEN_CACHE_KEY = 'access_token'


def get_access_token():
    """
    Retrieves the access token from the cache or requests a new one if it doesn't exist or has expired.

    Returns:
        str: Access token.
    """
    access_token = cache.get(TOKEN_CACHE_KEY)
    if not access_token:
        access_token, expiration_time = request_new_access_token()
        cache.set(TOKEN_CACHE_KEY, access_token, timeout=expiration_time)
    return access_token


def request_new_access_token():
    """
    Requests a new access token using client credentials.

    Returns:
        str: New access token.
    """
    token_url = app.config['TOKEN_URL']
    auth = HTTPBasicAuth(app.config['CLIENT_ID'], app.config['SECRET_ID'])
    response = requests.post(token_url, auth=auth)
    data = response.json()
    access_token = data.get('access_token')
    expiration_time = data.get('expires_in')
    return access_token, expiration_time


def provide_access_token(func):
    """
    Decorator that provides the access token as a keyword argument to the wrapped function.

    Args:
        func (function): The function to be wrapped.

    Returns:
        function: The wrapped function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = get_access_token()
        kwargs['access_token'] = access_token
        return func(*args, **kwargs)

    return wrapper


@provide_access_token
def get_actual_generations_per_unit(start_date, end_date, access_token):
    """
    Retrieves actual generation data for nuclear power units within the specified date range.

    Args:
        start_date (str): Start date in ISO format.
        end_date (str): End date in ISO format.
        access_token (str): Access token for authentication.

    Returns:
        dict: Actual generation data for nuclear power units.
    """
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


def transform_data(data):
    """
    Transforms the actual generation data into a pandas DataFrame.

    Args:
        data (list): Actual generation data.

    Returns:
        pandas.DataFrame: Transformed data.
    """
    df = pd.DataFrame(data)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    df["unit_eic_code"] = df["unit"].apply(lambda x: x["eic_code"])
    df["unit_name"] = df["unit"].apply(lambda x: x["name"])
    df["unit_production_type"] = df["unit"].apply(lambda x: x["production_type"])
    df = df[df['unit_production_type'] == 'NUCLEAR']
    df.drop(columns=["unit"], inplace=True)
    df = df.explode("values")
    df["value_start_date"] = pd.to_datetime(df["values"].apply(lambda x: x["start_date"]))
    df["value_end_date"] = pd.to_datetime(df["values"].apply(lambda x: x["end_date"]))
    df["value_updated_date"] = pd.to_datetime(df["values"].apply(lambda x: x["updated_date"]))
    df["value"] = df["values"].apply(lambda x: x["value"])
    df.drop(columns=["values"], inplace=True)
    return df


def production_average_per_hour(data):
    """
    Calculates the average value per hour from the transformed data.

    Args:
        data (list): Actual generation data.

    Returns:
        dict: Average values per hour.
    """
    df = transform_data(data)
    df['hour'] = df['value_start_date'].dt.hour
    df_hourly_avg = df.groupby('hour')['value'].mean()
    hourly_avg_dict = {}
    for hour, avg_value in df_hourly_avg.items():
        hourly_avg_dict[f"Hour {hour:02d}"] = avg_value
    return hourly_avg_dict


def production_sum_per_hour_of_day(data):
    """
    Calculates the sum of values per hour of each day from the transformed data.

    Args:
        data (list): Actual generation data.

    Returns:
        dict: Sum of values per hour of each day.
    """
    df = transform_data(data)
    df['hour'] = df['value_start_date'].dt.hour
    df_hourly_sum = df.groupby([df['value_start_date'].dt.date, df['hour']])['value'].sum()
    hourly_sum_dict = {}
    for (day, hour), sum_value in df_hourly_sum.items():
        day_str = day.strftime("%Y-%m-%d")
        if day_str not in hourly_sum_dict:
            hourly_sum_dict[day_str] = {}
        hourly_sum_dict[day_str][f"Hour {hour:02d}"] = sum_value
    return hourly_sum_dict


@app.route('/data')
def get_data():
    start_date = '2022-12-01T00:00:00+02:00'
    end_date = '2022-12-11T00:00:00+02:00'
    data = get_actual_generations_per_unit(start_date, end_date)
    return jsonify(data)


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
