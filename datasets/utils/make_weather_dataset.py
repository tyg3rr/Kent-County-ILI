from pyncei import NCEIBot, NCEIResponse
from datetime import date
import configparser
import pandas as pd
from epiweeks import Week

config = configparser.ConfigParser()
secrets = config.read('utils/secrets.ini')
my_token = config.get('default','ncdc_token')
ncei = NCEIBot(my_token, cache_name='ncei_cache', expire_after=3600)

def get_ncei_dataset(
                    dataset_id='GHCND'
                    ,station_id='GHCND:USW00094860'
                    ,datatype_ids=['TMIN','TMAX','TAVG','PRCP','AWND','SNOW']
                    ,start_date=date(2004,1,1)
                    ,end_date=date(2019,12,31)
                    ) -> pd.DataFrame:
    
    res = NCEIResponse()
    for year in range(start_date.year,end_date.year+1):
        res.extend(
            ncei.get_data(
                datasetid = dataset_id,
                stationid = station_id,
                datatypeid = datatype_ids,
                startdate = date(year,1,1),
                enddate = date(year,12,31),
                units='standard'
            )
        )
    return res.to_dataframe()

def format_dataset(df,term):
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = df['value'].apply(lambda x: round(x))
    df = df.pivot_table(values='value', index='date', columns=term)
    df.columns.name = None
    df = df.reset_index()
    df['epiweek'] = df['date'].apply(lambda x: Week.fromdate(x))
    df = df.set_index('epiweek').drop(columns=['date'])
    return df

def make_weather_dataset():
    df = get_ncei_dataset()[['date','datatype','value']]
    return format_dataset(df,'datatype')
