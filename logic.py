import json
import time
import requests
from kivy.app import App
from uk_covid19 import Cov19API

app = App().get_running_app()


def set_params(area):
    AREA_NAME = area.lower()
    filters = [
        # f'areaType=city',
        f'areaName={AREA_NAME}',
    ]
    return filters


structure = {
    "date": "date",
    "areaName": "areaName",
    "newCases": "newCasesByPublishDate",
    "newDeaths": "newDeathsByDeathDate",
}


def get_data(area):
    api = Cov19API(filters=set_params(area), structure=structure)
    data = api.get_json()
    df = api.get_dataframe()
    return data, df


def my_request(area):
    filters = ";".join(set_params(area))
    print(filters)
    req = requests.get(f'https://api.coronavirus.data.gov.uk/v1/data?filters={filters}&structure={json.dumps(structure)}')
    print(req.status_code)

if __name__ == "__main__":
    pass