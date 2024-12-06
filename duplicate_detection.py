import random

from data_tools import create_dataframe, create_dataframe_limited
from minhash_helpers import jaccard, generate_hash, signature_similarity, common_symbols, stopwords


def clean_all_symbols(line, symbol_list):
    # remove non ascii characters, https://stackoverflow.com/a/76931333/2912901
    if isinstance(line, float):
        line = str(line)
    line = line.encode('ascii', 'ignore').decode('ascii')
    for symbol in symbol_list:
        line = line.replace(symbol, ' ')
    return line

def clean_article(line):
    line = clean_all_symbols(line, common_symbols)
    line = line.lower()
    return line

def process_text_data(titles):
    cleaned_titles = []
    for t in titles:
        title = clean_article(t)
        cleaned_titles.append(title)
    
    terms = []
    term_map = {}
    term_sets = []
    for title in cleaned_titles:
        words = title.split()
        # words = [title[i:(i+3)] for i in range(0, len(title)-3)]  # create shingles
        term_set = list(set(words)) # just get unique words
        term_set = [word for word in term_set if word not in stopwords] # filter stop words
        # process to build term index
        for word in term_set:
            if word not in term_map:
                term_map[word] = len(terms)
                terms.append(word)
        term_sets.append(term_set)
    
    # see an example term set
    
    return cleaned_titles, term_sets, terms, term_map
     
def find_duplicates(df, col, ratings):
    random.seed(0)
    df = df[df[col].apply(lambda x: isinstance(x, str))]

    _, term_sets, terms, term_map = process_text_data(list(df[col]))
    # print('terms', len(terms))
    # print('term sets', len(term_sets))

    signature_size = 20

    hashes = []
    for i in range(signature_size):
        h = generate_hash(len(terms))
        hashes.append(h)
    
    # calculate the signatures for the names
    signatures = []
    for term_set in term_sets:
        signature = []
        index_set = list(map(lambda x: term_map[x], term_set))
        for h in hashes:
            vals = list(map(h, index_set))
            if len(vals) > 0:
                min_hash_value = min(list(map(h, index_set)))
            else:
                min_hash_value = -1
            signature.append(min_hash_value)
        signatures.append(signature)
    
    # convert the signature to a hash index and append the index, duplicate detection.
    binned_ids = {}
    n_bins = 10000000         # use a very large number here to make collisions unlikely (shared bin means near duplicate)
    for i in range(len(signatures)):
        # convert the sigature into a hashable tuple
        signature = tuple(signatures[i])
        bin = hash(signature) % n_bins
        if bin not in binned_ids:       # first hash to this bin? create a list.
            binned_ids[bin] = [i]
        else:
            binned_ids[bin].append(i)   # append this index to the existing bin.
    
    # # check the bins
    # print('unique bins', len(binned_ids))
    # input('press enter')
    dupes = []
    for bin in binned_ids:
        if len(binned_ids[bin]) > 1:
            # print(bin, binned_ids[bin])
            hashed_ids = binned_ids[bin]
            rating_set = {}
            for id in hashed_ids:
                r = list(ratings.loc[ratings['id'] == id]['rating'])
                if len(r) == 0:
                    rating_set[id] = -1
                else:
                    rating_set[id] = r[0]
            max_rated = max(rating_set, key=rating_set.get)
            hashed_ids.remove(max_rated)
            dupes.extend(hashed_ids)
    # print("duplicates to delete: ",len(dupes))
    return dupes

def remove_duplicates(recipes):
    # process the data
    ratings = create_dataframe('data/ratings_averages.csv')
    name_dupes = find_duplicates(recipes, 'name', ratings)
    desc_dupes = find_duplicates(recipes, 'description', ratings)
    u = list(set(name_dupes) | set(desc_dupes))
    filtered_recipes = recipes.drop(u)
    return filtered_recipes

def remove_ingr_duplicates(recipes, ingr_map):
    random.seed(0)

    _, term_sets, terms, term_map = process_text_data(list(ingr_map))
    # print('terms', len(terms))
    # print('term sets', len(term_sets))

    signature_size = 20

    hashes = []
    for i in range(signature_size):
        h = generate_hash(len(terms))
        hashes.append(h)
    
    # calculate the signatures for the names
    signatures = []
    for term_set in term_sets:
        signature = []
        index_set = list(map(lambda x: term_map[x], term_set))
        for h in hashes:
            vals = list(map(h, index_set))
            if len(vals) > 0:
                min_hash_value = min(list(map(h, index_set)))
            else:
                min_hash_value = -1
            signature.append(min_hash_value)
        signatures.append(signature)
    
    # convert the signature to a hash index and append the index, duplicate detection.
    binned_ids = {}
    n_bins = 10000000         # use a very large number here to make collisions unlikely (shared bin means near duplicate)
    for i in range(len(signatures)):
        # convert the sigature into a hashable tuple
        signature = tuple(signatures[i])
        bin = hash(signature) % n_bins
        if bin not in binned_ids:       # first hash to this bin? create a list.
            binned_ids[bin] = [i]
        else:
            binned_ids[bin].append(i)   # append this index to the existing bin.
    
    # # check the bins
    # print('unique bins', len(binned_ids))
    # input('press enter')
    ingr_indices = {key: index for index, key in enumerate(ingr_map)}
    for bin in binned_ids:
        if len(binned_ids[bin]) > 1:
            # print(bin, binned_ids[bin])
            hashed_ids = binned_ids[bin]
            deduped_index = ingr_indices[list(ingr_map)[hashed_ids[0]]]
            for i in range(len(hashed_ids)):
                ingr_indices[list(ingr_map)[hashed_ids[i]]] = deduped_index 
                
    ingr_freqs = {}
    for ings in recipes['ingredients']:
        for i in ings:
            i = ingr_indices[i]
            if i in ingr_freqs:
                ingr_freqs[i] += 1
            else:
                ingr_freqs[i] = 1
                
    recipes['ingredients'] = recipes['ingredients'].apply(lambda x: [ingr_indices[i] for i in x]) 
                    
    return recipes, ingr_indices, ingr_freqs