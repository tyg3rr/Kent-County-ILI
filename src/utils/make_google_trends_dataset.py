import pandas as pd
import json, math, requests, configparser
from datetime import date
from epiweeks import Week

cfg = configparser.ConfigParser()
secrets = cfg.read("utils/secrets.ini")

SERVER = 'https://www.googleapis.com/trends/'
VERSION = 'v1beta'
DISCOVERY_URL_SUFFIX = VERSION + '/timelinesForHealth?'
DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX

cat = '419'
geo = 'US-MI-563'
timeline_resolution = 'week'
my_key = cfg.get("default", "gtrends_apikey")
terms = ['flu','fever','cough','cold']
iso_start_date = '2004-01-01'
iso_end_date = '2019-12-31'

def url_builder(
                iso_start_date: str, 
                iso_end_date: str,
                terms: list,
                discovery_url = DISCOVERY_URL, 
                cat = cat, 
                geo = geo, 
                timeline_resolution = timeline_resolution, 
                key = my_key
                ) -> str:
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


def make_dataset(iso_start_date = iso_start_date,
                iso_end_date = iso_end_date,
                terms = terms,
                discovery_url = DISCOVERY_URL, 
                cat = cat, 
                geo = geo, 
                timeline_resolution = timeline_resolution, 
                key = my_key):
    
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


def format_dataset(df):
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = df['value'].apply(lambda x: round(x))
    df = df.pivot_table(values='value', index='date', columns='term')
    df.columns.name = None
    df = df.reset_index()
    df['epiweek'] = df['date'].apply(lambda x: Week.fromdate(x))
    df = df.set_index('epiweek').drop(columns=['date'])
    df = df.rename(columns={c:f'GS_{c}' for c in df.columns})
    return df


def make_google_trends_dataset(iso_start_date = iso_start_date,
                                iso_end_date = iso_end_date,
                                terms = terms,
                                discovery_url = DISCOVERY_URL, 
                                cat = cat, 
                                geo = geo, 
                                timeline_resolution = timeline_resolution, 
                                key = my_key
                                ):
    df = make_dataset(
                        iso_start_date=iso_start_date,
                        iso_end_date=iso_end_date,
                        terms=terms,
                        discovery_url=discovery_url,
                        cat=cat,
                        geo=geo,
                        timeline_resolution=timeline_resolution,
                        key=key
                    )
    return format_dataset(df)

