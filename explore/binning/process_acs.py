import pandas as pd
import numpy as np
from datetime import date
import tests

"""Goal: pull in ACS data. Output, for a unique state (WA)  x race combination, (black alone, black + asian, aian + nhpi + white, etc.),
a df in long format, with, for each [sex] x [single-year-age] x [state] x [year], the count of corresponding individuals residing in
the location
"""

def load_data(personurl, year):
    year = year
    IN_DIR = "/home/j/DATA/USA/AMERICAN_COMMUNITY_SURVEY"
    df = pd.read_csv(IN_DIR + '/' + str(year) + '/' + personurl) 
    df.columns = df.columns.map(str.lower)
    df_cols = ["serialno", "st", "pwgtp", "agep", "sex","racnum","racaian","racasn","racblk",
                "racnh","racpi","racsor","racwht","hisp"]
    return df.filter(items=df_cols)
    
def load_incoming_data(personurl, year):
    year = year
    IN_DIR = "/home/j/DATA/Incoming Data/USA/AMERICAN_COMMUNITY_SURVEY"
    df = pd.read_csv(IN_DIR + '/' + str(year) + '/' + "data/" + personurl)
    df.columns = df.columns.map(str.lower)
    df_cols = ["serialno", "st", "pwgtp", "agep", "sex","racnum","racaian","racasn","racblk",
                "racnh","racpi","racsor","racwht","hisp"]
    return df.filter(items=df_cols)

def format_acs(input_df, races, year, incl_hispanic = False):
    """input: raw ACS data for a state & year
       output: df with counts of people (using person weights) per state/year/sex/age/ethnicity/race bin 
    """
    #create copy of df
    df = input_df.copy(deep=True)
    
    #combine native hawaiian and pacific islander
    df['racnhpi'] = df[['racnh','racpi']].max(axis=1)
    df.drop(columns=['racnh','racpi'], inplace=True)
    
    #TEST sum of races == racnum
    all_races = ['racaian', 'racasn', 'racblk', 'racnhpi', 'racsor', 'racwht']
    df['race_count'] = df[all_races].sum(axis=1)
    assert(df[df.race_count!=df.racnum].shape[0]==0), "races in each row dont' sum to row total"
    
    #subset to races of interest
    df = df[df.race_count==len(races)]
    for i in races:
        df = df[df[i] > 0]
    
    #TEST: people exist in this category
    
    #remap vars
    df["hispanic"] = df['hisp'].map({1: 0,
                                     2: 1,
                                     3: 1,
                                     4: 1,
                                     5: 1,
                                     6: 1,
                                     7: 1,
                                     8: 1,
                                     9: 1,
                                     10: 1,
                                     11: 1,
                                     12: 1,
                                     13: 1,
                                     14: 1,
                                     15: 1,
                                     16: 1,
                                     17: 1,
                                     18: 1,
                                     19: 1,
                                     20: 1,
                                     21: 1,
                                     22: 1,
                                     23: 1,
                                     24: 1})
    
    df["state"] = df["st"].map({1: "AL",
                             2: "AK",
                             4: "AR",
                             5: "AZ",
                             6: "CA",
                             8: "CO",
                             9: "CT",
                             10: "DE",
                             11: "DC",
                             12: "FL",
                             13: "GA",
                             15: "HI",
                             16: "ID",
                             17: "IL",
                             18: "IN",
                             19: "IA",
                             20: "KS",
                             21: "KY",
                             22: "LA",
                             23: "ME",
                             24: "MD",
                             25: "MA",
                             26: "MI",
                             27: "MN",
                             28: "MS",
                             29: "MO",
                             30: "MT",
                             31: "NE",
                             32: "NV",
                             33: "NH",
                             34: "NJ",
                             35: "NM",
                             36: "NY",
                             37: "NC",
                             38: "ND",
                             39: "OH",
                             40: "OK",
                             41: "OR",
                             42: "PA",
                             44: "RI",
                             45: "SC",
                             46: "SD",
                             47: "TN",
                             48: "TX",
                             49: "UT",
                             50: "VT",
                             51: "VA",
                             53: "WA",
                             54: "WV",
                             55: "WI",
                             56: "WY",
                             72: "PR"})
    
    df["year"] = year
    
    df.rename(columns={"agep": "age",
                       "pwgtp": "weight",
                       "sex": "sex_id"
                      }, inplace=True)
    df.drop(["hisp","st","racnum"], axis=1, inplace=True)
    
    #drop hispanic, get population counts per race/ethnicity/sex/age
    if not incl_hispanic:
        df.drop(columns=['hispanic'], inplace=True) 
        df['pop_count'] = df.groupby(all_races + ['sex_id','age'])['weight'].transform('sum')
        df.drop(columns=['weight','serialno'], inplace=True)
        df.drop_duplicates(inplace=True)
        df = df[['state','year','sex_id','age'] + all_races + ['race_count','pop_count']]
    else:
        df['pop_count'] = df.groupby(all_races + ['hispanic','sex_id','age'])['weight'].transform('sum')
        df.drop(columns=['weight','serialno'], inplace=True)
        df.drop_duplicates(inplace=True)
        df = df[['state','year','sex_id','age','hispanic'] + all_races + ['race_count','pop_count']]
    
    df = df.sort_values(df.columns.tolist())
    
    return df

    #tests
    FINAL_COLS = ['state', 'year', 'sex_id', 'age', 'hispanic', 'racaian', 'racasn',
       'racblk', 'racnhpi', 'racsor', 'racwht', 'race_count', 'pop_count']
    
    assert (FINAL_COLS in df.columns)
    
    assert(df.state.dtype == 'O')

    for i in df.columns:
        if i == 'state':
            assert (df[i].dtype == 'O'), "Check location type"
        else:
            assert (df[i].dtype == 'int64'), "Check numeric type"

    return df

def add_decennial_age_bins(input_df, incl_hispanic = False):
    ''' merge on age groups and calculate proportion of age group each age comprises
    '''
    df = input_df.copy(deep=True)
    
    # add on age bin columns corresponding to decennial data
    age_starts = [0,5,10,15,18,20,21,22,25,30,35,40,45,50,55,60,62,65,67,70,75,80,85,120]
    df['age_bins'] = pd.cut(df.age, bins = age_starts, right=False, include_lowest=False, retbins=False)
    df['age_start'] = [i.left for i in df.age_bins]
    df['age_end'] = [i.right-1 for i in df.age_bins]
    
    # calculate proportion of age bin each age comprises
    all_races = ['racaian', 'racasn', 'racblk', 'racnhpi', 'racsor', 'racwht']
    if incl_hispanic:
        df['pop_denom'] = df.groupby(['state','year',
                                  'sex_id','hispanic',
                                  'age_start','age_end'] + all_races)['pop_count'].transform('sum')
    else:
        df['pop_denom'] = df.groupby(['state','year',
                                      'sex_id','age_start','age_end'] + all_races)['pop_count'].transform('sum')
        
    df['pop_proportion'] = df['pop_count'] / df['pop_denom']
    
    #clean up
    df.drop(columns=['age_bins','pop_denom'], inplace=True)
    
    #check
    df.groupby(['sex_id','age_start','age_end']).sum().pop_proportion.unique()
    
    return df