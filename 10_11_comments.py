# Explain n after each filter step

# Look into our filtering vs normalized filtering (make user/recipe matrix and z-score normalize)

import numpy as np
import pandas as pd
from data_tools import create_dataframe, standardize
from main import printOneVarStats


# map interactions to user as (recipe_id / rating) pairs
# for each user, standardize ratings to z-scores
# map ratings to recipes
# averate ratings

#            Names  Statistics
# 0            Min  -22.505293
# 1  0.25-Quantile   -0.339871
# 2         Median    0.157678
# 3           Mean   -0.109663
# 4  0.75-quantile    0.381631
# 5            Max    2.489451

def standardize_ratings(list):
    ratings = []
    for tuple in list:
        ratings.append(tuple[1])
    ratings = standardize(ratings)
    ret = []
    for i in range(len(list)):
        ret.append((list[i][0], ratings[i]))
    return ret

def map_interactions_to_user():
    interactions = create_dataframe('data/RAW_interactions.csv')[['user_id', 'recipe_id', 'rating']]
    # combine outputs them by key, append them to a list
    combiner = {}
    for row in interactions.iterrows():
        k,v = row[1].iloc[0], (row[1].iloc[1], row[1].iloc[2])
        if k not in combiner:
            combiner[k] = [v]
        else:
            combiner[k].append(v)
    key_list = list(combiner.keys())
    key_list.sort()
    tuples = []
    for k in key_list:
        if len(combiner[k]) > 1:
            tuples.append( (k, combiner[k]) )
    
    print(tuples)
    
    normalized_recipe_tuples = []
    for _, vs in tuples:
        [normalized_recipe_tuples.append(i) for i in standardize_ratings(vs)]
    
    print(normalized_recipe_tuples)
    
    df = pd.DataFrame({'ids': np.array([i[0] for i in normalized_recipe_tuples]), 'ratings': np.array([i[1] for i in normalized_recipe_tuples])})
    combiner = {}
    for row in df.iterrows():
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
        
    print(combined_recipe_tuples)
    data = {'id': np.array([i[0] for i in combined_recipe_tuples]), 'rating': np.array([i[1] for i in combined_recipe_tuples])}
    df = pd.DataFrame(data)
    # print(df)
    # print(len(df.query('rating > 0')))
    printOneVarStats(df['rating'])
    return combined_recipe_tuples

def create_recipe_matrix():
    interactions = create_dataframe('data/RAW_interactions.csv')
    recipes = create_dataframe('data/RAW_recipes.csv')
    matrix = [] # need to create 2D array - can't be len users bc there's missing ids
    
    for recipe in recipes:
        for interaction in interactions.query("recipe_id == "+str(recipe['id'])):
            matrix[interaction['user_id']][recipe['id']] = interactions['rating']
    
    return matrix

def normalize_ratings(x): # need to filter out 0s accordingly
    for user in x:
        user = standardize(user)
    return x

def average_ratings(x):
    pass

# Construct tests (input and get list, see if there are issues with that list)

# Weight similarity by .85 and novelty by .25

# Maximize ingredient similarity, minimize title/other similarity

# To test, apply this to a real world situation (parent’s pantry)

# Strict vs relaxed matching

# Weighting for tags (boost, hide, etc)

map_interactions_to_user()