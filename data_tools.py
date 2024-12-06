from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

def create_dataframe(filepath):
    df = pd.read_csv(filepath, delimiter=',')
    return df

def create_dataframe_limited(filepath, nrows):
    df = pd.read_csv(filepath, delimiter=',', nrows=nrows)
    return df

def standard_deviation(x):
    n = len(x)
    sum_value = np.sum(np.square(x - np.mean(x)))/(n - 1)
    return np.sqrt(sum_value)

def standardize(x):
    if len(x) == 1:
        return [0]
    m = np.mean(x)
    sd = standard_deviation(x)
    if sd == 0:
        return [0 for _ in range(len(x))]
    return (x - m)/sd

def plot_bottom_75(ingr_freqs):
    arr = np.array(list(ingr_freqs.values()))
    percentile_25 = np.percentile(arr, 75)
    # Get the values below the 25th percentile
    bottom_75 = arr[arr <= percentile_25]
    plt.hist(bottom_75)
    plt.title('Ingredient Frequency Distribution')
    plt.xlabel('Ingredient Frequency')
    plt.show()

def avg_num_ingrs(ingr_lists):
    return np.mean([len(i) for i in ingr_lists])

def printOneVarStats(col):
    # construct a data frame:
    labels = ['Min','0.25-Quantile','Median','Mean', '0.75-quantile', 'Max']
    stats = [np.min(col), np.quantile(col,0.25), np.median(col),
                np.mean(col), np.quantile(col,0.75), np.max(col)]
        
    summary_df = pd.DataFrame({'Names':labels, 'Statistics':stats})
    print(summary_df)
    