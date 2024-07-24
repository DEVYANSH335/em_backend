from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import io
import logging
import os

app = Flask(__name__)
CORS(app)

# Load database configuration from environment variables
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)

def analyze_data(table_name):
    try:
        df = pd.read_sql_table(table_name, engine)
        summary = df.describe().to_dict()
        return jsonify(summary)
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Failed to analyze data"}), 500

def upload_excel(file):
    try:
        excel_data = pd.read_excel(file)
        summary = excel_data.describe().to_dict()
        buffer = io.BytesIO()
        file.save(buffer)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            attachment_filename='uploaded_file.xlsx'
        )
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Failed to upload file"}), 500

@app.route('/data-analysis/<table_name>', methods=['GET'])
def data_analysis(table_name):
    return analyze_data(table_name)

@app.route('/upload-excel', methods=['POST'])
def upload_excel_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    return upload_excel(file)

if __name__ == '__main__':
    app.run(debug=True)