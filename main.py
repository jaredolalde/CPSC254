from model import DataModel
from view import DataView
from controller import DataController
from adapter import JSONDataAdapter
from data_fetcher import DataFetcher
from datetime import datetime

def main():
    json_directory = 'data'
    data_adapter = JSONDataAdapter()

    model = DataModel(json_directory, data_adapter)
    view = DataView()
    controller = DataController(model, view)

    controller.run()

if __name__ == "__main__":
    main()