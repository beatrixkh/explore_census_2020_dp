import numpy as np, pandas as pd

rename = {'P0030004_SF':'aian_alone_sf',
          'P0030004_DP':'aian_alone_dp_old',
          'P0060004_SF':'aian_in_combo_sf',
          'P0060004_DP':'aian_in_combo_dp_old',
          'P0010001_SF':'all_pop_sf',
          'P0010001_DP':'all_pop_dp_old',
          'P0010001':'all_pop',
          'H7X004_sf':'aian_alone_sf',
          'H7X004_dp':'aian_alone_dp_new',
          'H7X005_sf':'asian_alone_swapping',
          'H7X005_dp':'asian_alone_new_das',
          'P0030005':'asian_alone_old_das'}
    
def pull_data_aian(path, usecols, groupvar):
    """pull csv from path, using usecols,
    and then agg and sum using groupvar"""
    
    df = pd.read_csv(path, usecols = usecols)
    df = df.groupby(groupvar).sum()
    
    df = df.rename(columns=rename).reset_index()
    
    return df

def add_loc_cols(df):
	"""assuming the formatting of the jun20 DAS state files, add location cols
	"""

	df['STATE'] = [int(i[1:3]) for i in df.gisjoin]
	df['COUNTY'] = [int(i[4:7]) for i in df.gisjoin]
	df['TRACT'] = [int(i[7:-4]) for i in df.gisjoin]
	df['BLOCK'] = [int(i[-4:]) for i in df.gisjoin]

	if df.STATE[0] > 9:
		raise Exception("Warning! Code might be incorrect for states with fips code > 9")

	return df