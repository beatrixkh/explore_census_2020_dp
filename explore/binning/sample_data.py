import pandas as pd, numpy as np

def generate_single_year_df(input_df, age_distribution):
    ''' takes in a df with geoid/sex_id/age-bins
        outputs df with geoid/sex_id/single-year-ages
    '''
    # subset to rows of interest / rows with positive population
    input_df = input_df[input_df.pop_count>0]
    
    # initialize output df with pop_counts == 0
    df = input_df[['geoid','sex_id']].drop_duplicates()
    
    for i in np.arange(121):
        var = str(i)
        df[var] = 0

    df = df.melt(id_vars = ['geoid','sex_id'],
                 value_vars = [str(i) for i in np.arange(121)],
                 var_name='age', value_name = 'pop_count')

    df.age = df.age.astype('int64')
    
    # fill pop_count
    for i, row in input_df.iterrows():
        geoid = row.geoid
        sex_id = row.sex_id
        single_years = sample_data(row, age_distribution)
        for i in single_years:
            df.loc[(df.age==i) & (df.sex_id==sex_id) & (df.geoid==geoid),'pop_count'] +=1
    
    # test
#     assert(input_df.pop_count.sum()==df.pop_count.sum()), 'Total population mismatch'
    
    assert(input_df.geoid.nunique()==df.geoid.nunique()), 'Geoid mismatch'
    
    return df

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


    