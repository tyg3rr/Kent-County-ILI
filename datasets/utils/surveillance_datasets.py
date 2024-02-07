import pandas as pd
from datetime import datetime
from epiweeks import Week
from os import path
import configparser
cfg = configparser.ConfigParser()
cfg.read('utils/secrets.ini')
ROOT_PATH = path.abspath(cfg.get('default','root'))
DATA_PATH = path.join(ROOT_PATH, 'src/data')

names = [
        "cases 2000 to 2004.csv",
        "cases 2005 to 2009.csv",
        "cases 2010 to 2014.csv",
        "cases 2015 to 2019.csv",
        "cases 2019 to 2023.csv"
        ]

FILES = [path.join(DATA_PATH, file_name) for file_name in names]

def make_incidence_dataset(files: list = FILES) -> pd.DataFrame:
    data = pd.DataFrame()
    for f in files:
        d = pd.read_csv(f, skiprows=6)
        d.columns = d.iloc[0,] 
        d = d.loc[d['County'] == 'Kent',]\
                    .reset_index()\
                    .drop(columns=['index','Region','County','Total']).T\
                    .rename(columns={0:'cases'})
        d.index.name = 'date'
        data = pd.concat([d,data])
    data = data.reset_index()
    data['epiweek'] = data['date']\
                        .apply(lambda x:
                        Week.fromstring(
                        f"{x.split('-')[1]}-{x.split('-')[0]}"))

    return data.set_index('epiweek').drop(columns=['date'])

def make_syndromic_dataset(syndromic_file = path.join(DATA_PATH, 'MSSS.csv')) -> pd.DataFrame:

    df = pd.read_csv(syndromic_file, usecols=['Admitted'])
    df['visits'], df['Admitted'] = 1, pd.to_datetime(df['Admitted'])
    df['epiweek'] = df['Admitted'].apply(lambda x: Week.fromdate(x))
    
    return pd.DataFrame(df.groupby('epiweek')['visits'].sum())

