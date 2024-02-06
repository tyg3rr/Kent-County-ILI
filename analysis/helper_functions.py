import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from datetime import date
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error


def train_test_validate_split(df: pd.DataFrame, end_train: date, end_validation: date):
    '''
    Returns end_train, end_validation, df_train, df_val, df_test
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
    feature_importances = forecaster.get_feature_importances().set_index('feature')
    feature_importances = feature_importances.loc[feature_importances['importance']>0]
    feature_importances['abs'] = feature_importances.apply(abs)
    feature_importances = feature_importances.sort_values(by='abs',ascending=False).drop(columns=['abs'])
    return feature_importances

def metrics(preds, actual):
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
    Format and print Ad-Fuller test output
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

def results_summary_to_dataframe(results):
    '''take the result of an statsmodel results table and transforms it into a dataframe'''
    pvals = results.pvalues
    coeff = results.params
    conf_lower = results.conf_int()[0]
    conf_higher = results.conf_int()[1]

    results_df = pd.DataFrame({"pvals":pvals,
                                "coeff":coeff,
                                "conf_lower":conf_lower,
                                "conf_higher":conf_higher
                                })
    #Reordering...
    results_df = results_df[["coeff","pvals","conf_lower","conf_higher"]]
    return results_df


def plot_ccf_manual(target, exog, nlags=10):
    """PLot CCF using manual calculations"""
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
    """ Lag-N cross correlation. 
    Shifted data (y) filled with NaNs 
    Parameters
    ----------
    lag : int, default 0
    x, y : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    return x.corr(y.shift(lag))