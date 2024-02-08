import pandas as pd
import json, math, requests, configparser
from datetime import date
from epiweeks import Week

cfg = configparser.ConfigParser()
secrets = cfg.read("utils/secrets.ini")

def url_builder(
                iso_start_date: str = '2004-01-01', 
                iso_end_date: str = '2019-12-31',
                terms: list = ['flu','fever','cough','cold'],
                discovery_url: str = 'https://www.googleapis.com/trends/v1beta/timelinesForHealth?', 
                cat: str = '419', 
                geo: str = 'US-MI-563', 
                timeline_resolution: str = 'week', 
                key: str = cfg.get("default", "gtrends_apikey")
                ) -> str:
    """
    Builds a URL for querying Google Trends API with the specified parameters.

    Args:
        iso_start_date (str): The start date in ISO format (YYYY-MM-DD). Default is '2004-01-01'.
        iso_end_date (str): The end date in ISO format (YYYY-MM-DD). Default is '2019-12-31'.
        terms (list): A list of search terms. Default is ['flu','fever','cough','cold'].
        discovery_url (str): The base URL for the Google Trends API. Default is 'https://www.googleapis.com/trends/v1beta/timelinesForHealth?'.
        cat (str): The category ID for health-related topics. Default is '419'.
        geo (str): The geographic location for the query. Default is 'US-MI-563'.
        timeline_resolution (str): The resolution of the timeline data. Default is 'week'.
        key (str): The API key for accessing the Google Trends API. Default is fetched from the configuration file.

    Returns:
        str: The complete URL for querying the Google Trends API with the specified parameters.
    """
    arguments = [
        discovery_url
        ,''.join([f'terms={t}&' for t in terms])
        ,f'time.startDate={iso_start_date}'
        ,f'&time.endDate={iso_end_date}' 
        ,f'&timelineResolution={timeline_resolution}'
        ,f'&geo={geo}'
        ,f'&cat={cat}'
        ,f'&key={key}'
        ,'&alt=json']
    return f"{''.join([arg for arg in arguments])}"


def make_dataset(
                iso_start_date: str = '2004-01-01', 
                iso_end_date: str = '2019-12-31',
                terms: list = ['flu','fever','cough','cold'],
                discovery_url: str = 'https://www.googleapis.com/trends/v1beta/timelinesForHealth?', 
                cat: str = '419', 
                geo: str = 'US-MI-563', 
                timeline_resolution: str = 'week', 
                key: str = cfg.get("default", "gtrends_apikey")
                ) -> pd.DataFrame:
    """
    Fetches Google Trends data for specified terms and date range.
    
    Args:
        iso_start_date (str): The start date in ISO format (YYYY-MM-DD). Default is '2004-01-01'.
        iso_end_date (str): The end date in ISO format (YYYY-MM-DD). Default is '2019-12-31'.
        terms (list): The list of terms to fetch data for. Default is ['flu','fever','cough','cold'].
        discovery_url (str): The URL for Google Trends API. Default is 'https://www.googleapis.com/trends/v1beta/timelinesForHealth?'.
        cat (str): The category parameter for Google Trends API. Default is '419'.
        geo (str): The geographic location parameter for Google Trends API. Default is 'US-MI-563'.
        timeline_resolution (str): The resolution of the timeline data. Default is 'week'.
        key (str): The API key for accessing Google Trends API. Default is fetched from configuration file.
        
    Returns:
        pd.DataFrame: The fetched Google Trends data as a pandas DataFrame.
    """
    
    data = pd.DataFrame()

    start_year = date.fromisoformat(iso_start_date).year
    end_year = date.fromisoformat(iso_end_date).year
    nyears = (end_year - start_year)
    nterms = len(terms)
    ncalls = math.ceil((52 * nyears * nterms) / 2000)
    iter_years = math.ceil(nyears / ncalls)

    for i in range(start_year, end_year+1, iter_years):
        url = url_builder(f'{i}-01-01', f'{i + iter_years - 1}-12-31', terms)
        res = requests.get(url)    
        contents = json.loads(res.content)['lines']
        for j in range(0,len(contents)):
            df = pd.json_normalize(contents[j]['points'],meta=['value', 'date'])
            df['term'] = contents[j]['term']
            data = pd.concat([data, df])
    return data


def format_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats the given DataFrame by performing the following operations:
    1. Converts the 'date' column to datetime format.
    2. Rounds the 'value' column to the nearest integer.
    3. Pivots the DataFrame using 'date' as the index, 'term' as the columns, and 'value' as the values.
    4. Resets the column names and index.
    5. Converts the 'date' column to epiweek format using the Week.fromdate() function.
    6. Sets the 'epiweek' column as the new index and drops the 'date' column.
    7. Renames the columns by prefixing 'GS_' to each column name.

    Args:
        df (pd.DataFrame): The input DataFrame to be formatted.

    Returns:
        pd.DataFrame: The formatted DataFrame.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = df['value'].apply(lambda x: round(x))
    df = df.pivot_table(values='value', index='date', columns='term')
    df.columns.name = None
    df = df.reset_index()
    df['epiweek'] = df['date'].apply(lambda x: Week.fromdate(x))
    df = df.set_index('epiweek').drop(columns=['date'])
    df = df.rename(columns={c:f'GS_{c}' for c in df.columns})
    return df


def make_google_trends_dataset() -> pd.DataFrame:
    """
    Creates a Google Trends dataset by making use of the `make_dataset` and `format_dataset` functions.

    Returns:
        pd.DataFrame: The formatted Google Trends dataset.
    """
    df = make_dataset()
    return format_dataset(df)

