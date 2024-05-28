from flask import Flask, jsonify
from datetime import datetime, timedelta
import pymysql
import numpy as np
import joblib
import os

app = Flask(__name__)

host = os.getenv('DATABASE_HOST')
user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
database = os.getenv('DATABASE_NAME')

model = joblib.load('model.pkl')

def fetch_data_for_week(start_date):
    end_date = start_date + timedelta(days=6)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()
    query = f"SELECT date, rate FROM rates WHERE date BETWEEN '{start_date_str}' AND '{end_date_str}'"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data

def preprocess_data(data):
    rates = [round(float(row[1]), 2) for row in data]

    preprocessed_data = np.zeros((1, 7))
    preprocessed_data[0] = rates[::-1]

    return preprocessed_data

def store_predictions(predictions, start_date):
    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()
    for i in range(7):
        prediction_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        rate = float(predictions[0][i])  # Ensure each prediction is a float
        cursor.execute("INSERT INTO predictions (date, rate, created_at, updated_at) VALUES (%s, %s,CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (prediction_date, rate))
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/')
def hello_world():
    return jsonify({
        'project': 'Exchange Rate Predictions (USD-MKD)',
        'routes': {
            'root': '/',
            'prediction': '/predict',
            'weekly_prediction': '/weekly_predict'
        }
    })

@app.route('/predict', methods=['GET'])
def predict():
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday() + 7)
    data = fetch_data_for_week(start_date)
    if len(data) == 7:
        preprocessed_data = preprocess_data(data)
        predictions = model.predict(preprocessed_data)
        rounded_predictions = np.round(predictions, 2)

        return jsonify({'predictions': rounded_predictions.tolist()}), 200
    else:
        return jsonify({'error': 'Not enough data for predictions'}), 400

@app.route('/weekly_predict', methods=['GET'])
def weekly_predict():
    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(date) FROM rates")
    min_date = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(date) FROM rates")
    max_date = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    start_date = min_date
    while start_date <= max_date:
        data = fetch_data_for_week(start_date)
        if len(data) == 7:
            preprocessed_data = preprocess_data(data)
            predictions = model.predict(preprocessed_data)
            rounded_predictions = np.round(predictions, 2)
            store_predictions(rounded_predictions, start_date + timedelta(days=7))
        start_date += timedelta(days=7)

    return jsonify({'status': 'Predictions updated for all weeks'}), 200

if __name__ == '__main__':
    app.run()
