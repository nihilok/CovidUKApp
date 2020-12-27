import json
import time

import pandas as pd
import requests
from kivy.app import App
from uk_covid19 import Cov19API

app = App().get_running_app()


def set_params(area, area_type=None):
    AREA_NAME = area.lower()
    AREA_TYPE = f'areaType={area_type.lower()}' if area_type else ''
    filters = [
        AREA_TYPE,
        f'areaName={AREA_NAME}',
    ]
    return filters


structure = {
    "date": "date",
    "areaName": "areaName",
    "newCases": "newCasesByPublishDate",
    "newDeaths": "newDeathsByDeathDate",
    "newDeathsByPublishDate": "newDeathsByPublishDate",
}

all_nations_structure = {
    "date": "date",
    "name": "areaName",
    "code": "areaCode",
    "cases": {
        "daily": "newCasesByPublishDate",
        "cumulative": "cumCasesByPublishDate"
    },
    "deaths": {
        "daily": "newDeathsByPublishDate",
        "cumulative": "cumDeathsByDeathDate"
    }
}


def get_data(area, area_type=None):
    nations = ['england', 'wales', 'scotland', 'northern ireland']
    if area == 'all':
        nations_df = pd.concat([Cov19API(filters=set_params(nation), structure=structure).get_dataframe() for nation in nations])
        nations_df = nations_df.groupby('date').sum()
        data = nations_df.to_json()
        df = nations_df
        print(data)
        return data, df
    else:
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