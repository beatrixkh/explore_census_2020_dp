import pandas as pd, numpy as np

def sample_data(row, age_distribution):
    ''' for each row of data, corresponding to a specific sex/race/ethnicity/age-bin:
        generate single-year age samples from ACS age distribution
    '''
    #get specific vals
    size = row.pop_count
    sex = row.sex_id
    age_bin = row.age_start

    # get corresponding vals & probabilities
    vals = age_distribution[(age_distribution.sex_id==sex) & (age_distribution.age_start==age_bin)].age.tolist()
    probs = age_distribution[(age_distribution.sex_id==sex) & (age_distribution.age_start==age_bin)].pop_proportion.tolist()
    
    # draw random specific ages
    return np.random.choice(a=vals, p=probs, size = size)

