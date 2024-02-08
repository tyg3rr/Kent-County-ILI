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
    """
    Retrieves weather data from the NCEI dataset for a specific station and time period.
    
    Args:
        dataset_id (str): The ID of the dataset to retrieve. Default is 'GHCND'.
        station_id (str): The ID of the weather station to retrieve data from. Default is 'GHCND:USW00094860'.
        datatype_ids (list): A list of datatype IDs to retrieve. Default is ['TMIN','TMAX','TAVG','PRCP','AWND','SNOW'].
        start_date (datetime.date): The start date of the data to retrieve. Default is January 1, 2004.
        end_date (datetime.date): The end date of the data to retrieve. Default is December 31, 2019.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the retrieved weather data.
    """
    
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

def format_dataset(df, term):
    """
    Formats the dataset by converting the 'date' column to datetime,
    pivoting the dataframe based on the given term, setting the column
    names, resetting the index, converting the 'date' column to epiweek,
    and dropping the 'date' column.

    Parameters:
    df (DataFrame): The input dataframe.
    term (str): The term to pivot the dataframe on.

    Returns:
    DataFrame: The formatted dataframe.
    """
    df['date'] = pd.to_datetime(df['date'])
    df = df.pivot_table(values='value', index='date', columns=term)
    df.columns.name = None
    df = df.reset_index()
    df['epiweek'] = df['date'].apply(lambda x: Week.fromdate(x))
    df = df.set_index('epiweek').drop(columns=['date'])
    return df

def make_weather_dataset():
    """
    Creates a weather dataset by extracting relevant columns from the NCEI dataset.

    Returns:
        pandas.DataFrame: The formatted weather dataset.
    """
    df = get_ncei_dataset()[['date','datatype','value']]
    return format_dataset(df,'datatype')
