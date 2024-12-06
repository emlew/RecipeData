"""
    Here are some classes for Map Reduce functionality.
"""
import pandas as pd
import numpy as np

from data_tools import create_dataframe

class Mapper():
    """
        This function is called to do the work.
        It will produce the key value data
    """
    def process(self):
        pass

class Reducer():
    """
        This function is called to do the reduce pairs
    """
    def reduce(self, pairs):
        pass

class MapReduceJob():
    def __init__(self, mapper, reducer) -> None:
        self.mapper = mapper
        self.reducer = reducer

    def run(self):
        intermediate_result = self.mapper.process()
        sorted_result = MapReduceJob.combine(intermediate_result)
        result = self.reducer.reduce(sorted_result)
        return result
        
    @staticmethod
    def combine(df):
        # combine outputs them by key, append them to a list
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
        output_tuples = []
        for k in key_list:
            output_tuples.append( (k, combiner[k]) )
        return output_tuples

class RatingMapper(Mapper):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    def process(self):
        output = []
        df = create_dataframe(self.filename)
        return df[['recipe_id', 'rating']]
        
class MeanReducer(Reducer):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def reduce_func(alist):
        return np.mean(alist)
    
    def reduce(self, pairs):
        output_tuples = []
        for k, vs in pairs:
            output_tuples.append((k, MeanReducer.reduce_func(vs)))
    
        return output_tuples

def get_ratings():
    mapper = RatingMapper('data/RAW_interactions.csv')
    reducer = MeanReducer()
    job = MapReduceJob(mapper, reducer)
    results = job.run()
    ids = []
    ratings = []
    for result in results:
        ids.append(result[0])
        ratings.append(result[1])
    data = {'ids': np.array(ids), 'ratings': np.array(ratings)}
    df = pd.DataFrame(data)
    return df

def make_ingredient_array(ingredients):
    term_array = []
    for term in ingredients.split(", "):
        stripped_term = term.replace('[','').replace(']','').replace("'",'').replace('"','')
        if stripped_term != 'salt':
            term_array.append(stripped_term)
    return (set(term_array))

class IngredientMapper(Mapper):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    def process(self):
        df = create_dataframe(self.filename)
        ingredients = []
        counts = []
        for row in df.iterrows():
            ingr_array = make_ingredient_array(row[1]['ingredients'])
            for ingredient in ingr_array:
                ingredients.append(ingredient)
                counts.append(1)
        data = {'ingredient': np.array(ingredients), 'count': np.array(counts)}
        df = pd.DataFrame(data)
        return df
        
class SumReducer(Reducer):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def reduce_func(alist):
        if alist == []:
            return 0
        else:
            value = alist[0]
            rest = alist[1:]
            return value + SumReducer.reduce_func(rest)    
    def reduce(self, pairs):
        output_tuples = []
        for k, vs in pairs:
            # use len instead of reduce_func to avoid a recursion error
            output_tuples.append((k, len(vs)))
        return output_tuples

def get_ingredient_freqs():
    mapper = IngredientMapper('data/RAW_recipes.csv')
    reducer = SumReducer()
    job = MapReduceJob(mapper, reducer)
    results = job.run()
    names = []
    freqs = []
    for result in results:
        names.append(result[0])
        freqs.append(result[1])
    data = {'name': np.array(names), 'frequency': np.array(freqs)}
    df = pd.DataFrame(data)
    return df

get_ingredient_freqs()