import numpy as np
import pandas as pd
from data_tools import create_dataframe, standardize

def standardize_ratings(list):
    ratings = []
    for tuple in list:
        ratings.append(tuple[1])
    ratings = standardize(ratings)
    ret = []
    for i in range(len(list)):
        ret.append((list[i][0], ratings[i]))
    return ret

def has_multiple_ratings(pair):
    _, value = pair
    return (len(value) > 1)

def combine_by_user_id(x):
    # combine ratings by user id and return all users that have more than one rating
    combiner = {}
    for row in x.iterrows():
        k,v = row[1].iloc[0], (row[1].iloc[1], row[1].iloc[2])
        if k not in combiner:
            combiner[k] = [v]
        else:
            combiner[k].append(v)
    return dict(filter(has_multiple_ratings, combiner.items()))

def normalize_by_user(x):
    # normalize ratings by for each user and return list of recipes with standardized scores
    normalized = []
    for _,v in x.items():
        [normalized.append(t) for t in standardize_ratings(v)]
    return normalized

def combine_by_recipe(x):
    # find mean rating for each recipe based on list of recipes and ratings
    combiner = {}
    for row in x.iterrows():
        k,v = row[1].iloc[0], row[1].iloc[1]
        if k not in combiner:
            combiner[k] = [v]
        else:
            combiner[k].append(v)
    key_list = list(combiner.keys())
    key_list.sort()
    # Combiner output
    combined_recipe_tuples = []
    for k in key_list:
        combined_recipe_tuples.append( (k, np.mean(combiner[k])) )
    return combined_recipe_tuples
  
def create_ratings_summary(ratings):
    labels = ['Min','0.25-Quantile','Median','Mean', '0.75-quantile', 'Max']
    stats = [np.min(ratings), np.quantile(ratings,0.25), np.median(ratings),
                np.mean(ratings), np.quantile(ratings,0.75), np.max(ratings)]
    summary_df = pd.DataFrame({'Names':labels, 'Statistics':stats})
    return summary_df
    
def map_interactions_to_user():
    interactions = create_dataframe('data/RAW_interactions.csv')[['user_id', 'recipe_id', 'rating']]
    combined_ratings = combine_by_user_id(interactions)
    normalized_ratings = normalize_by_user(combined_ratings)
    
    ratings_df = pd.DataFrame({'id': np.array([i[0] for i in normalized_ratings]), 'rating': np.array([i[1] for i in normalized_ratings])})
    average_ratings = combine_by_recipe(ratings_df)
    data = {'id': np.array([i[0] for i in average_ratings]), 'rating': np.array([i[1] for i in average_ratings])}
    average_ratings_df = pd.DataFrame(data)
    # print(create_ratings_summary(average_ratings_df['rating']))
    average_ratings_df.to_csv("data/ratings_averages.csv")

map_interactions_to_user()