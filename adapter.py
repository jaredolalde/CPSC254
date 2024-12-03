import json
import os
import pandas as pd
from datetime import datetime

class JSONDataAdapter:
    def load_data(self, directory, symbol):
        filename = f'{symbol.lower()}_data_2021-01-01_{datetime.now().date()}.json'
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"File {filename} not found in {directory}.")
            return None

        with open(filepath, 'r') as f:
            data = json.load(f)
        return data

class CSVDataAdapter:
    def load_data(self, directory, symbol):
        filename = f'{symbol.lower()}_data_2021-01-01_{datetime.now().date()}.csv'
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"File {filename} not found in {directory}.")
            return None

        data = pd.read_csv(filepath)
        return data.to_dict('records')