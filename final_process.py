from collections import Counter, defaultdict
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, Birch, KMeans
from sklearn.decomposition import PCA
from data_tools import create_dataframe_limited
from duplicate_detection import remove_duplicates, remove_ingr_duplicates
from kmeans_clustering import make_ingredient_array


def plot_pca_2d(X_data, result):
    pca_model = PCA(2)
    pca_model.fit(X_data)
    X = pca_model.transform(X_data)
    
    plt.scatter(X[:,0], X[:,1], c=result.labels_)
    for i in range(X_data.shape[0]):
        x = X[i,0]
        y = X[i,1]
        name = result.labels_[i]
        plt.text(x,y, name, fontsize=7)
    
    centers_X = pca_model.transform(pd.DataFrame(result.cluster_centers_))
    plt.scatter(centers_X[:,0], centers_X[:,1],marker='x')
    plt.xlabel('PC 1')
    plt.ylabel('PC 2')
    plt.show()

def gini_impurity(cluster_tags):
    """Calculate the Gini impurity for a cluster based on tag counts."""
    total_tags = len(cluster_tags)
    if total_tags == 0:
        return 0  # No impurity if no tags
    
    # Calculate the proportion of each tag
    tag_counts = Counter(cluster_tags)
    gini = 1 - sum((count / total_tags) ** 2 for count in tag_counts.values())
    
    return gini

def main():
    # read recipe file
    full_recipes = create_dataframe_limited('data/RAW_recipes.csv', 30000)

    # remove duplicate recipes based on name and description 
    full_recipes = remove_duplicates(full_recipes)
    print('duplicates removed. new num recipes:',len(full_recipes))
    
    # parse ingredient string into array of ingredient strings
    ingrs, ingr_freqs = make_ingredient_array(full_recipes['ingredients'])
    recipes = pd.DataFrame({'id': full_recipes['id'], 'ingredients': ingrs})

    # consolidate duplicate ingredients
    recipes, ingr_map, ingr_freqs = remove_ingr_duplicates(recipes, ingr_freqs.keys())
    print('ingredient duplicates removed. new num ingr:',len(ingr_freqs))
    
    # remove any ingredients used only once
    bottom_bound = np.quantile(list(ingr_freqs.values()), 0.3)
    top_bound = np.quantile(list(ingr_freqs.values()), 0.7)
    non_unique_ingrs = [k for k,v in ingr_freqs.items() if v > bottom_bound and v < top_bound]
    
    recipes['ingredients'] = recipes['ingredients'].apply(lambda x: [i for i in x if i in non_unique_ingrs]) 
    print('singular ingredients removed. new num ingr:',len(non_unique_ingrs))

    # calculate idfs
    n = len(ingr_freqs.items())
    idfs = {k: np.log2(n/v) for k,v in ingr_freqs.items() if v > 1} 
    print('idfs calculated.')
    
    # map ingredients to their index
    id_maps = {}
    for (i, recipe) in recipes['id'].items():
        id_maps[recipe] = i
    df = pd.DataFrame(id_maps.items())
    df.to_csv("data/ingr_map_2.csv", header=False, index=False)
    print('recipe map created.')
    
    # create matrix and write to 'data/recipe_ingr_matrix.csv'
    # create_recipe_ingr_matrix(recipes, idfs)
    m = []
    print('making matrix')
    # recipes = recipes.sample(frac=(1/10),axis=0)    

    for i in range(len(recipes)):
        if (i%100 == 0):
            print(i)
        # Extract the list of ingredients for the recipe
        rec_ingredients = recipes.iloc[i]['ingredients']
        
        # Initialize the row with zeros for all ingredients
        row = [0] * len(idfs)
        
        # Update row values based on ingredient presence
        for ingredient in rec_ingredients:
            if ingredient in idfs:
                # Set the matrix cell to the ingredient's IDF value
                row[list(idfs.keys()).index(ingredient)] = idfs[ingredient]
        
        # Add the completed row to the matrix
        m.append(row)
    print('matrix created and saved to data/recipe_ingr_matrix.csv.')
    
    
    # create clusters
    # m = pd.read_csv('data/recipe_ingr_matrix.csv', delimiter=',', header=None, index_col=False)
    # map = pd.read_csv('data/ingr_map_2.csv', delimiter=',', header=None, index_col=False)

    kmeans_model = KMeans(n_clusters=122,n_init='auto')
    result = kmeans_model.fit(m[:1000])
    
    # Store the labels
    labels = result.labels_
    

    all_labels = result.predict(m)
    
    # Group data point indices by their cluster label
    clusters = defaultdict(list)
    for idx, label in enumerate(all_labels):
        clusters[label].append(idx)

    # Convert clusters to a regular dictionary (optional)
    clusters = dict(clusters)

    cluster_impurities = {}
    
    for cluster_id, recipe_indices in clusters.items():
        # Gather all tags for recipes in this cluster
        cluster_tags = []
        for index in recipe_indices:
            cluster_tags.extend(recipes.iloc[index]['ingredients'])  # Assuming tags[index] is a list of tags for that recipe
            
        # Calculate the Gini impurity for the cluster
        cluster_impurities[cluster_id] = gini_impurity(cluster_tags)
    
    for cluster_id, recipe_indices in clusters.items():
        if len(recipe_indices) > 4 and len(recipe_indices) < 20 and cluster_impurities[cluster_id] < 0.5:
            print("------------------",cluster_id,"------------------")
            print(cluster_impurities[cluster_id])
            for index in recipe_indices:
                # print(recipes.iloc[index])
                print(full_recipes.iloc[index])
    
    return
    
    plt.hist(cluster_impurities.values())
    plt.title('Cluster Impurity Distribution - Ingredients')
    plt.xlabel('Cluster Impurity')
    plt.show()
    
    for cluster_id, recipe_indices in clusters.items():
        # Gather all tags for recipes in this cluster
        cluster_tags = []
        for index in recipe_indices:
            cluster_tags.extend(full_recipes.iloc[index]['tags'])  # Assuming tags[index] is a list of tags for that recipe
            
        # Calculate the Gini impurity for the cluster
        cluster_impurities[cluster_id] = gini_impurity(cluster_tags)
    
    plt.hist(cluster_impurities.values())
    plt.title('Cluster Impurity Distribution - Tags')
    plt.xlabel('Cluster Impurity')
    plt.show()
        
    
       
main()
