import pandas as pd
import numpy as np
import math
from os import path
import configparser
from epiweeks import Week
from datetime import date, datetime
from calendar import month_name, month_abbr
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from datetime import date
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error

# Reading Secrets
# ======================================================
cfg = configparser.ConfigParser()
cfg.read('secrets.ini')
ROOT_PATH = path.abspath(cfg.get('default','root'))
DATA_PATH = path.join(ROOT_PATH, 'datasets/data')


def fetch_preprocess_dataset(file: str = 'raw_dataset.csv', 
                            col_ordered: set = 
                                            (
                                            'cases','visits','GS_cold', 
                                            'GS_cough', 'GS_fever', 'GS_flu', 
                                            'AWND', 'PRCP', 'SNOW', 
                                            'TMAX', 'TMIN', 'TAVG',
                                            'Overall AQI Value',
                                            'CO', 'Ozone', 'PM10', 
                                            'PM25', 'Days Good',
                                            'Days Moderate', 'Days Unhealthy'
                                            )
                            ):
    """
    Fetches and preprocesses the dataset.

    Args:
        file (str): The name of the dataset file. Default is 'raw_dataset.csv'.
        col_ordered (set): The ordered set of column names. Default is a predefined set of column names.

    Returns:
        pandas.DataFrame: The preprocessed dataset.
    """
    df = pd.read_csv(path.join(DATA_PATH, file))
    df['epiweek'] = df['epiweek'].map(lambda x: Week.fromstring(str(x)))
    df['weekstart'] = pd.to_datetime(df['epiweek'].map(lambda x: Week.startdate(x)))
    df.set_index('weekstart', inplace=True)
    df['epiweek'] = df['epiweek'].map(lambda x: int(str(x)[4:]))

    means = df[list(col_ordered)].groupby(df.index.month).mean()
    means.index.name = 'month'
    df['month'] = df.index.month

    df = df.reset_index().set_index(['weekstart','month'])

    df['TAVG'] = df[['TAVG']].fillna(
                            pd.DataFrame(
                            (df['TMAX'] + df['TMIN']) / 2)\
                            .rename(columns={0:'TAVG'})
                                )

    df[list(col_ordered)] = df[list(col_ordered)].fillna(means)

    df['Main Pollutant'] = df['Main Pollutant'].astype('category') # One-hot encoding 'Main Pollutant'
    df = pd.get_dummies(df)\
    .drop(columns=["Main Pollutant_['Ozone' 'PM2.5']"])

    epiweek_encoded = cyclical_encoding(df['epiweek'].apply(lambda x: x-1), cycle_length=52)  # Cyclical encoding 'epiweek' to capture 
    df = pd.concat([df, epiweek_encoded], axis=1)                                             # the cyclic nature of weeks in a year
    df = df.reset_index().set_index('weekstart').drop(columns=['month']).resample('W').first().fillna(method='ffill')
        
    return df

def train_test_validate_split(df: pd.DataFrame, end_train: date, end_validation: date):
    '''
    Splits the input DataFrame into training, validation, and test sets based on the specified end dates.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame to be split.
        end_train (date): The end date for the training set.
        end_validation (date): The end date for the validation set.
    
    Returns:
        tuple: A tuple containing the end dates, and the split DataFrames for training, validation, and test sets.
    '''
    
    if df.index.freq == None:
        print('Your data has no frequency. Resample and try again.')
        return None
    
    df_train = df.loc[:end_train,:]
    df_val = df.loc[end_train:end_validation,:]
    df_test = df.loc[end_validation:,:]

    print(f"Dates train      : {df_train.index.min()} --- {df_train.index.max()}  (n={len(df_train)})")
    print(f"Dates validacion : {df_val.index.min()} --- {df_val.index.max()}  (n={len(df_val)})")
    print(f"Dates test       : {df_test.index.min()} --- {df_test.index.max()}  (n={len(df_test)})")

    return end_train, end_validation, df_train, df_val, df_test

def describe_features(forecaster):
    """
    Returns a DataFrame containing the feature importances of a forecaster.

    Parameters:
    forecaster (object): The forecaster object for which to compute feature importances.

    Returns:
    pandas.DataFrame: DataFrame containing the feature importances, sorted by importance in descending order.
    """
    feature_importances = forecaster.get_feature_importances().set_index('feature')
    feature_importances = feature_importances.loc[feature_importances['importance']>0]
    feature_importances['abs'] = feature_importances.apply(abs)
    feature_importances = feature_importances.sort_values(by='abs',ascending=False).drop(columns=['abs'])
    return feature_importances

def metrics(preds, actual):
    """
    Calculate the mean absolute error (MAE) and root mean squared error (RMSE) between predicted values and actual values.

    Args:
        preds (array-like): Predicted values.
        actual (array-like): Actual values.

    Returns:
        tuple: A tuple containing the MAE and RMSE.
    """
    mae = mean_absolute_error(actual, preds)
    rmse = math.sqrt(mean_squared_error(actual, preds))
    return mae, rmse



def cyclical_encoding(data: pd.Series, cycle_length: int) -> pd.DataFrame:
    """
    Encode a cyclical feature with two new features sine and cosine.
    The minimum value of the feature is assumed to be 0. The maximum value
    of the feature is passed as an argument.
    
    Parameters
    ----------
    data : pd.Series
        Series with the feature to encode.
    cycle_length : int
        The length of the cycle. For example, 12 for months, 24 for hours, etc.
        This value is used to calculate the angle of the sin and cos.
    Returns
    -------
    result : pd.DataFrame
        Dataframe with the two new features sin and cos.
    """

    sin = np.sin(2 * np.pi * data/cycle_length)
    cos = np.cos(2 * np.pi * data/cycle_length)
    result =  pd.DataFrame({
                f"{data.name}_sin": sin,
                f"{data.name}_cos": cos
            })

    return result


def ADF(time_series, max_lags):
    """
    Calculate and print the results of the Augmented Dickey-Fuller (ADF) test.

    Parameters:
    time_series (array-like): The time series data to be tested.
    max_lags (int): The maximum number of lags to consider in the test.

    Returns:
    None

    Prints:
    ADF Statistic: The test statistic value.
    p-value: The p-value of the test.
    lags: The number of lags used in the test.
    Critical Values: The critical values at different confidence levels.
    """
    t_stat, p_value, lags, _, critical_values, _ = adfuller(
                                                            time_series,
                                                            maxlag=max_lags
                                                            )
    print(f'ADF Statistic: {t_stat:.2f}')
    print(f'p-value: {p_value:.2f}')
    print(f'lags: {lags}')
    for key, value in critical_values.items():
        print('Critial Values:')
        print(f'   {key}, {value:.2f}')


def plot_ccf_manual(target, exog, nlags=10):
    """
    Plot Cross Correlation Function (CCF) using manual calculations.

    Parameters:
    target (Series): The target time series.
    exog (Series): The exogenous time series.
    nlags (int): Number of lags to consider in the CCF calculation. Default is 10.

    Returns:
    None
    """
    lags = []
    ccfs = []
    for i in np.arange(0,nlags+1):
        lags.append(i)
        ccfs.append(crosscorr(target, exog, lag=i))

    _ = plt.stem(lags, ccfs, use_line_collection=True)
    _ = plt.title(f"Cross Correlation (Manual): {target.name} & {exog.name}")
    plt.show()
    plt.close()

def crosscorr(x: pd.Series, y: pd.Series, lag: int=0) -> float:
    """
    Lag-N cross correlation.
    
    Calculates the cross correlation between two pandas.Series objects, x and y, with a specified lag.
    The data in y is shifted by the lag value and filled with NaNs.
    
    Parameters
    ----------
    x : pandas.Series
        The first series for cross correlation.
    y : pandas.Series
        The second series for cross correlation.
    lag : int, optional
        The lag value for shifting the data in y. Default is 0.
    
    Returns
    -------
    crosscorr : float
        The cross correlation value between x and y with the specified lag.
    """
    return x.corr(y.shift(lag))