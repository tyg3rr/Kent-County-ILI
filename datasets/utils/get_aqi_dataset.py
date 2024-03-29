import pandas as pd
import numpy as np
from datetime import datetime
from epiweeks import Week
from os import path
import configparser
cfg = configparser.ConfigParser()
cfg.read('utils/secrets.ini')

def get_aqi_dataset() -> pd.DataFrame:
    """
    Retrieves the Air Quality Index (AQI) dataset.

    Returns:
        pd.DataFrame: The AQI dataset containing the following columns:
            - epiweek: The epidemiological week.
            - Overall AQI Value: The overall AQI value.
            - Main Pollutant: The main pollutant.
            - CO: Carbon monoxide level.
            - Ozone: Ozone level.
            - PM10: Particulate matter (PM10) level.
            - PM25: Particulate matter (PM2.5) level.
            - Days_Good: Number of days with good air quality.
            - Days_Moderate: Number of days with moderate air quality.
            - Days_Unhealthy: Number of days with unhealthy air quality.
    """
    ROOT_PATH = path.abspath(cfg.get('default','root'))
    DATA_PATH = path.join(ROOT_PATH, 'src/data')
    dd = pd.concat(
        [pd.read_csv(path.join(DATA_PATH, f'aqidaily{year}.csv')) for year in range(2005,2020)])
    dd = dd[['Date','Overall AQI Value','Main Pollutant','CO','Ozone','PM10','PM25']]
    for poll in ['CO','Ozone','PM10','PM25']:
        dd[poll] = pd.to_numeric(dd[poll], errors='coerce')
    dd['Date'] = pd.to_datetime(dd['Date'])
    dd['epiweek'] = dd['Date'].map(lambda x: Week.fromdate(x))
    dd = dd.set_index('epiweek').drop(columns=['Date'])
    dd['aqi'] = pd.cut(dd['Overall AQI Value'], 
                        bins=[0,50,100,200],
                        labels=['Good','Moderate','Unhealthy'])
    dd = pd.get_dummies(dd, columns=['aqi'], prefix=['Days '], prefix_sep=[''])

    dd = dd.groupby('epiweek').aggregate(lambda x: 
                                        x.mode() if x.dtype == 'O' 
                                        else x.sum() if x.name[0:4] == 'Days'
                                        else x.mean())
    return dd.round()