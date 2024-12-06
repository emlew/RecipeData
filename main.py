from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt # plotting
import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd

from map_reduce_tools import get_ingredient_freqs, get_ratings

def createHist(x, x_label):    
    plt.hist(x)
    plt.title(x_label+' Distribution')
    plt.xlabel(x_label)
    plt.show()

def printOneVarStats(col):
    # construct a data frame:
    labels = ['Min','0.25-Quantile','Median','Mean', '0.75-quantile', 'Max']
    stats = [np.min(col), np.quantile(col,0.25), np.median(col),
                np.mean(col), np.quantile(col,0.75), np.max(col)]
        
    summary_df = pd.DataFrame({'Names':labels, 'Statistics':stats})
    print(summary_df)

def plotIngredientsAndSteps(df):
    ingredients = df['n_ingredients']
    steps = df['n_steps']
    plt.scatter(x=ingredients, y=steps)
    plt.xlabel('Ingredients')
    plt.ylabel('Steps')
    plt.show()
    
def plotIngredientsStepsMinutes(df):
    ingredients = df['n_ingredients']
    steps = df['n_steps']
    fig = plt.figure()
    # get a plot handle for more control
    ax = fig.add_subplot(projection='3d')
    ax.scatter(xs=ingredients, ys=steps, zs=df['minutes'])
    ax.set_xlabel('Ingredients')
    ax.set_ylabel('Steps')
    ax.set_zlabel('Minutes')
    plt.show()

def get_terms_term_map(term_sets):
    terms = []
    term_map = {}
    for term_set in term_sets:
        for term in term_set.split(", "):
            stripped_term = term.replace('[','').replace(']','').replace("'",'')
            if stripped_term not in term_map:
                term_map[stripped_term] = len(terms)
                terms.append((stripped_term, 1))
            else:
                terms[term_map[stripped_term]] = (stripped_term, terms[term_map[stripped_term]][1] + 1)
    return terms, term_map

def make_ingredient_array(ingredients):
    term_array = []
    for term in ingredients.split(", "):
        stripped_term = term.replace('[','').replace(']','').replace("'",'')
        term_array.append(stripped_term)
    return (set(term_array))

# cosine distance (1 - cosine similarity)
def cosine_distance(a,b):
    # this is another way to calculate consine simiarity.
    # note for a vector v, the square root of v dot v is v's vector length
    return 1 - np.dot(a, b) / (np.sqrt(np.dot(a, a)) * np.sqrt(np.dot(b, b)))

def euclidean_distance(a,b):
    return len(a & b) / len(a | b)

def write_signif_pairs_euclidean(recipes, names):
    pairs = []
    for i in range(len(recipes)):
        r_i = make_ingredient_array(recipes[i])
        for j in range(i+1, len(recipes)):
            r_j = make_ingredient_array(recipes[j])
            corr = euclidean_distance(r_i, r_j)
            if (corr > 0.5):
                pairs.append((names[i], names[j], corr))
    return pairs
    # write_pairs('data/corrs.txt', pairs)  

def get_all_pairs_euclidean(recipes, names):
    pairs = []
    for i in range(len(recipes)):
        r_i = make_ingredient_array(recipes[i])
        for j in range(i+1, len(recipes)):
            r_j = make_ingredient_array(recipes[j])
            corr = euclidean_distance(r_i, r_j)
            pairs.append((names[i], names[j], corr))
    write_pairs('data/corrs.txt', pairs)

def write_pairs(filepath, pair_list):
    '''
    This is a simple function that writes the data to a text file.
    '''
    with open(filepath, 'w') as f:
        for a,b,c in pair_list:
            f.write(f'{a}\t{b}\t{c}\n')

def main():
    # printFilenames()
    # df = createDataframe('data/RAW_recipes.csv')
    # column_names = df.columns
    # print(column_names)
    # print(df)
    # createRatingsHist(get_ratings().query('ratings > 3')['ratings'])
    df = get_ingredient_freqs()
    freqs = df['frequency']
    printOneVarStats(freqs)
    # createHist(freqs, 'Ingredient Frequency')
    createHist(df.query('frequency < 29')['frequency'], 'Ingredient Frequency')
    # ingredient_nums = df['n_ingredients']
    # # printOneVarStats(ingredient_nums)
    # plt.hist(ingredient_nums)
    # # plt.show()
    
    # print(printOneVarStats(get_avg_ratings(df)))
    # recipes = df['ingredients']
    # names = df['name']
    
    # get_all_pairs_euclidean(recipes, names)
    # filepath = "data/corrs.txt"
    # corr_df = pd.read_table(filepath, sep='\t', header=None)
    # # set the header columns ourselves.
    # corr_df.columns = ['node_A', 'node_B', 'corr']
    # plt.hist(corr_df['corr'])
    # plt.show()
    
    
    
    # terms, term_map = get_terms_term_map(recipes)
    # ingredient_df = pd.DataFrame({"Ingredients":[term[0] for term in terms], "Uses":[term[1] for term in terms]})
    # subset = ingredient_df.query("Uses > 85700")
    # print(subset)
    # printOneVarStats(ingredient_df['Uses'])
    # plt.hist(ingredient_df['Uses'], bins=8000)
    # plt.ylim(0,100)
    # plt.show()
        
