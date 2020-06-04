import pandas as pd, numpy as np

input_dir = '/home/j/temp/beatrixh/sim_science/decennial_census_2010/'
location_cols = ['STATE', 'COUNTY', 'TRACT', 'BLKGRP', 'BLOCK']

race_alone_totals = ['P003000' + str(i) for i in range(1,9)]

sex_by_age = ['P012000' + str(i) for i in range(1,9)] + ['P01200' + str(i) for i in range(10,50)] #all races
sex_by_age_white_alone =['P012A00' + str(i) if i<10 else 'P012A0' + str(i) for i in range(1,50)]
sex_by_age_black_alone = ['P012B00' + str(i) if i<10 else 'P012B0' + str(i) for i in range(1,50)]
sex_by_age_aian_alone = ['P012C00' + str(i) if i<10 else 'P012C0' + str(i) for i in range(1,50)]
sex_by_age_asian_alone = ['P012D00' + str(i) if i<10 else 'P012D0' + str(i) for i in range(1,50)]
sex_by_age_nhpi_alone = ['P012E00' + str(i) if i<10 else 'P012E0' + str(i) for i in range(1,50)]
sex_by_age_otherrace_alone = ['P012F00' + str(i) if i<10 else 'P012F0' + str(i) for i in range(1,50)]
sex_by_age_mixed_race = ['P012G00' + str(i) if i<10 else 'P012G0' + str(i) for i in range(1,50)]

    
def read_decennial(race_specific_sex_by_age = sex_by_age_asian_alone, path = 'WA2010DHCCSV/WA2010DHC.CSV'):
    df = pd.read_csv(input_dir + path, usecols = location_cols + race_specific_sex_by_age)
    df = df[df.BLOCK.notna()]
    
    #cast race vars to long format
    df = df.melt(id_vars = location_cols, value_vars = race_specific_sex_by_age)
    
    # CHECK that individ. age bins sum to totals!
    
    # subset to all age-specific vars (get rid of both-sex-all-age)
    df = df[df.variable.str[-2:]!='01']
    
    # cleaning
    df = rename_census_ages(df)
    df = add_geoid(df)
    df = df[~df.variable.str[-2:].isin(['02','26'])] #combine this with prev step if rewrite rename_census_ages
    
    df.drop(columns=location_cols + ['var_key'], inplace=True)
    
    return df
    
def add_geoid(input_df):
    """ input shape: has ['STATE','COUNTY','TRACT','BLOCK'] with dtypes [int,float,float,float]
        rewrite this for states/tracts/counties with different str(int(x)) lengths
    """
    df = input_df.copy(deep=True)
    df['geoid'] = df.STATE.astype(str) + df.COUNTY.astype(str).str[:-2] + df.TRACT.astype(str).str[:-2] + df.BLOCK.astype(str).str[:-2]
    
    #test len(i) for i in df.geoid == 15
    
    return df

def rename_census_ages(input_df):
    """ This is for the 5-ish year age bins and vars of the form 'P012[A/B/.../G]0'
    """
    df = input_df.copy(deep=True)
    df['var_key'] = df.variable.str[:4] + df.variable.str[5:]
    if df.var_key.nunique()!=48:
        raise Exception("Oops; variable col doesn't contain expected vals")
        
    df['var_key'] = df.var_key.str[-2:].astype(int)
    
    
    # map census var names into something readable
    age_start = [0,5,10,15,18,20,21,22,25,30,35,40,45,50,55,60,62,65,67,70,75,80,85]
    age_end = [i-1 for i in age_start[1:]] + [120]

    age_start = [0] + age_start
    age_end = [120] + age_end

    age_start_dict = {}
    age_end_dict = {}
    sex_dict = {}

    counter = 0
    for i in np.arange(2,26):
        age_start_dict[i] = age_start[counter]
        age_end_dict[i] = age_end[counter]
        sex_dict[i] = 1
        counter += 1
        
    counter = 0
    for i in np.arange(26,50):
        age_start_dict[i] = age_start[counter]
        age_end_dict[i] = age_end[counter]
        sex_dict[i] = 2
        counter += 1

    df['age_start'] = df.var_key.map(age_start_dict)
    df['age_end'] = df.var_key.map(age_end_dict)
    df['sex_id'] = df.var_key.map(sex_dict)
    return df