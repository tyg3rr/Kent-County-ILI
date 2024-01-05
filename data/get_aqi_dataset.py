import pandas as pd
import numpy as np
from datetime import datetime
from epiweeks import Week

def get_aqi_dataset() -> pd.DataFrame:

    dd = pd.concat(
        [pd.read_csv(f'aqidaily{year}.csv') for year in range(2005,2020)])
    dd = dd[['Date','Overall AQI Value','Main Pollutant','CO','Ozone','PM10','PM25']]
    for poll in ['CO','Ozone','PM10','PM25']:
        dd[poll] = pd.to_numeric(dd[poll], errors='coerce')
    dd['Date'] = pd.to_datetime(dd['Date'])
    dd['epiweek'] = dd['Date'].map(lambda x: Week.fromdate(x))
    dd = dd.set_index('epiweek').drop(columns=['Date'])
    dd = dd.groupby('epiweek').aggregate(lambda x: x.mode() if x.dtype == 'O' else x.mean())
    return dd.round()