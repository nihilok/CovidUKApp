import json
import time

import pandas as pd
import requests
from kivy.app import App
from uk_covid19 import Cov19API

from kivy_garden.graph import Graph, MeshLinePlot

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
        nations_df['newDeaths'].fillna(int(0), inplace=True)
        # nations_df['date'] = pd.to_datetime(nations_df['date'])
        # nations_df.set_index('date', inplace=False)
        for index, row in nations_df.iterrows():
            if not row['newDeaths']:
                row['newDeaths'] += row['newDeathsByPublishDate']
                row['newDeaths'] = int(row['newDeaths'])
        nations_df = nations_df.groupby('date').sum()
        data = nations_df.to_dict()
        df = nations_df
        return data, df
    else:
        api = Cov19API(filters=set_params(area), structure=structure)
        data = api.get_json()
        df = api.get_dataframe()
        return data, df

def plot_graph(x,y):
    ticker_list = ['newCases', 'newDeaths']
    tickers_on_plot = ['newCases', 'newDeaths']
    max_y = 0
    for line in y:
        if max(line) > max_y:
            max_y = max(line)
    plot_colors = [[1, 1, 0, 1], [1, 0, 0, 1]]
    graph = Graph(ylabel='Cases/Deaths', y_grid_label=True,
                  x_grid_label=False, padding=5, x_grid=True, y_grid=True, xmax=30, ymin=0, ymax=max_y)
    x_nums = [i for i in range(1,31)]
    for i, line in enumerate(y):
        plot = MeshLinePlot(color=plot_colors[i])
        plot.points = [(i,j) for i, j in zip(x_nums,line[-30:])]
        graph.add_plot(plot)
    return graph

def my_request(area):
    filters = ";".join(set_params(area))
    print(filters)
    req = requests.get(f'https://api.coronavirus.data.gov.uk/v1/data?filters={filters}&structure={json.dumps(structure)}')
    print(req.status_code)


if __name__ == "__main__":
    pass
