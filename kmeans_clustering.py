from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from data_tools import create_dataframe

def distance(a, b):
    return np.sqrt(np.sum((b-a)**2))

def gini_impurity(df, model):
    # get cluster centers and calc freq for each
    total = len(df)
    centers = model.cluster_centers_
    freqs = []
    for i in range(len(centers)):
        subset = len(df.iloc[model.labels_==i,])/total
        freqs.append(subset*subset)
    return 1 - np.sum(freqs)

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

def make_ingredient_array(all_ingredients):
    chars_to_remove = ['[', ']', "'", '"']
    ingr_lists = []
    ingr_set = []
    ingr_map = {}
    for ingredients in all_ingredients:
        term_array = []
        for term in ingredients.split(", "):
            stripped_term = ''.join([char for char in term if char not in chars_to_remove])
            term_array.append(stripped_term)
            ingr_set.append(stripped_term)
            if stripped_term in ingr_map:
                ingr_map[stripped_term] += 1
            else:
                ingr_map[stripped_term] = 1
        ingr_lists.append(term_array)
    ingr_set = list(set(ingr_set))
    return ingr_lists, ingr_map

def calculate_idfs(all_ingredients):
    n_recipes = all_ingredients.count()
    combiner = {}
    for ingredients in all_ingredients:
        for ingredient in ingredients:
            if ingredient not in combiner:
                combiner[ingredient] = [1]
            else:
                combiner[ingredient].append(1)
    key_list = list(combiner.keys())
    key_list.sort()
    # Combiner output
    output_tuples = []
    for k in key_list:
        output_tuples.append( (k, np.log2(n_recipes / np.sum(combiner[k]))) )
    return pd.DataFrame({'ingredient': [i[0] for i in output_tuples], 'freq': [i[1] for i in output_tuples]}) 
    
def create_recipe_ingr_matrix(recipes, idfs):
    matrix = []
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
        matrix.append(row)
    # pca_model = PCA(139)
    # pca_model.fit(matrix)
    # X = pca_model.transform(matrix)
    pd.DataFrame(matrix).to_csv("data/recipe_ingr_matrix.csv", header=False, index=False)
    
def create_recipe_ingr_matrix_old():
#     recipes = create_dataframe('data/RAW_recipes.csv')
#     recipes = pd.DataFrame({'id': recipes['id'], 'ingredients': make_ingredient_array(recipes['ingredients'])})
#     freqs = calculate_idfs(recipes['ingredients'])
#     id_maps = {}
#     for (i, recipe) in recipes['id'].items():
#         id_maps[recipe] = i
#     matrix = np.zeros((len(recipes), len(freqs)))
#     print('making matrix')
#     for i in range(len(recipes)):
#         print(i)
#         for j in range(len(freqs)):
#             if freqs['ingredient'][j] in recipes['ingredients'][i]:
#                 matrix[i][j] = freqs['freq'][j]
#     df = pd.DataFrame(matrix)
#     df.to_csv("data/recipe_ingr_matrix.csv", header=False, index=False)
    pass

def kmeans_visualization():
    m = pd.read_csv('data/recipe_ingr_matrix.csv', delimiter=',', header=None, index_col=False)
    print(m.shape)
    to_try = list(range(110,125))
    cluster_sum_squared_distance = []
    cluster_sum_impurities = []
    avg_cluster_sizes = []
    print('trying ks:')
    for k in to_try:
        print(k)
        kmeans_model = KMeans(n_clusters=k,n_init='auto')
        result = kmeans_model.fit(m)
        total_within_squared_distances = 0
        cluster_sizes = []
        # plot_pca_2d(m, result)
        
        for i in range(k):
            center = result.cluster_centers_[i]
            subset = m.iloc[result.labels_==i,]
            distances_to_centroid = subset.apply(lambda x: distance(x, center), axis=1)
            total_within_squared_distances += np.sum(distances_to_centroid**2)
            cluster_sizes.append(len(subset))
        
        # append fitness to list.
        cluster_sum_impurities.append(gini_impurity(m, result))
        cluster_sum_squared_distance.append(total_within_squared_distances)
        avg_cluster_sizes.append(np.mean(cluster_sizes))
        
    plt.plot(to_try, cluster_sum_squared_distance)
    plt.xlabel('value of k')
    plt.ylabel('Within Cluster Sum of Squared Distances')
    plt.show()    
    
    plt.plot(to_try[1:], np.diff(cluster_sum_squared_distance))
    plt.xlabel('value of k')
    plt.ylabel('diff of Within Cluster Sum of Squared Distances')
    plt.show()
    
    plt.plot(to_try, avg_cluster_sizes)
    plt.xlabel('value of k')
    plt.ylabel('Average Cluster Size')
    plt.show()

def kmeans_visualization_old():
    m = pd.read_csv('data/recipe_ingr_matrix.csv', delimiter=',', header=None, index_col=False, nrows=300)
    print(m.shape)
    to_try = list(range(2,50))
    cluster_sum_squared_distance = []
    cluster_sum_impurities = []
    print('trying ks:')
    for k in to_try:
        print(k)
        kmeans_model = KMeans(n_clusters=k,n_init='auto')
        result = kmeans_model.fit(m)
        total_within_squared_distances = 0
        # plot_pca_2d(m, result)
        
        for i in range(k):
            center = result.cluster_centers_[i]
            subset = m.iloc[result.labels_==i,]
            distances_to_centroid = subset.apply(lambda x: distance(x, center), axis=1)
            total_within_squared_distances += np.sum(distances_to_centroid**2)
        
        # append fitness to list.
        cluster_sum_impurities.append(gini_impurity(m, result))
        cluster_sum_squared_distance.append(total_within_squared_distances)
    
    plt.plot(to_try, cluster_sum_squared_distance)
    plt.xlabel('value of k')
    plt.ylabel('Within Cluster Sum of Squared Distances')
    plt.show()    
    
    plt.plot(to_try[1:], np.diff(cluster_sum_squared_distance))
    plt.xlabel('value of k')
    plt.ylabel('diff of Within Cluster Sum of Squared Distances')
    plt.show()
    
    plt.plot(to_try, cluster_sum_impurities)
    plt.xlabel('value of k')
    plt.ylabel('Within Cluster Impurity')
    plt.show()

def main():
    # create_recipe_ingr_matrix()
    kmeans_visualization()
    return
