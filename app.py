from flask import Flask, jsonify
from datetime import datetime, timedelta
import pymysql
import numpy as np
import joblib

app = Flask ( __name__ )

host = 'localhost'
user = 'sail'
password = 'password'
database = 'laravel'

model = joblib.load ( 'model.pkl' )


def fetch_data_from_database ():
    connection = pymysql.connect ( host=host,
                                   user=user,
                                   password=password,
                                   database=database )
    cursor = connection.cursor ( )

    end_date = datetime.now ( )
    start_date = end_date - timedelta ( days=7 )
    start_date_str = start_date.strftime ( '%Y-%m-%d' )
    end_date_str = end_date.strftime ( '%Y-%m-%d' )

    query = f"SELECT date, rate FROM rates WHERE date BETWEEN '{start_date_str}' AND '{end_date_str}'"
    cursor.execute ( query )
    data = cursor.fetchall ( )

    cursor.close ( )
    connection.close ( )

    return data


def preprocess_data ( data ):
    rates = [ round ( float ( row [ 1 ] ), 2 ) for row in data ]

    preprocessed_data = np.zeros ( (len ( rates ) - 6, 7) )
    for i in range ( 6, len ( rates ) ):
        preprocessed_data [ i - 6 ] = rates [ i - 6:i + 1 ] [ ::-1 ]

    return preprocessed_data



@app.route ( '/' )
def hello_world ():
    return jsonify ( {
        'project': 'Exchange Rate Predictions (USD-MKD)',
        'routes': {
            'root': '/',
            'prediction': '/predict'
        }
    } )


@app.route ( '/predict', methods=[ 'GET' ] )
def predict ():
    data = fetch_data_from_database ( )
    preprocessed_data = preprocess_data ( data )
    predictions = model.predict ( preprocessed_data )

    # Round each prediction to two decimal places
    rounded_predictions = np.round ( predictions, 2 )

    return jsonify ( { 'predictions': rounded_predictions.tolist ( ) } ), 200


if __name__ == '__main__':
    app.run ( )
