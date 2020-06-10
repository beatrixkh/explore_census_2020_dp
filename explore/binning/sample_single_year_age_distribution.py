import pandas as pd, numpy as np

from process_acs import *
from process_decennial import *
from sample_data import *

def main(state, races, start, stop, decennial_path = 'WA2010DHCCSV/WA2010DHC.CSV'):
    races = races.split(sep=',')
    decennial_races_dict = {'racaian':sex_by_age_aian_alone,
    'racasn':sex_by_age_asian_alone,
    'racblk':sex_by_age_black_alone,
    'racnhpi':sex_by_age_nhpi_alone,
    'racsor':sex_by_age_otherrace_alone,
    'racwht':sex_by_age_white_alone
    }

    if len(races) > 1:
        decennial_races_var = sex_by_age_mixed_race
    else:
        decennial_races_var = decennial_races_dict[races[0]]

    # get age distribution from ACS
    age_distribution = load_incoming_data(state)
    age_distribution = format_acs(age_distribution, races = races, years = age_distribution.year.unique().tolist())
    age_distribution = add_decennial_age_bins(age_distribution)
    
    decennial = read_decennial(race_specific_sex_by_age = decennial_races_var, path = decennial_path)

    # subset to positive-population rows
    decennial_subset = decennial[decennial.pop_count > 0]
    decennial_subset = decennial_subset.iloc[start:stop,]

    # sample single-year ages from ACS using decennial super structure
    single_years_df = generate_single_year_df(decennial_subset, age_distribution=age_distribution)
    
    # add back in location_cols
    single_years_df['state'] = single_years_df.geoid.str[:2]
    single_years_df['county'] = single_years_df.geoid.str[2:5]
    single_years_df['tract'] = single_years_df.geoid.str[5:11]
    single_years_df['blkgrp'] = single_years_df.geoid.str[11:]
    single_years_df.drop(columns=['geoid'], inplace=True)

    #final order
    final_cols = ['state','county','tract','blkgrp','sex_id','age','pop_count']
    output = single_years_df.filter(items=final_cols)

    # save to csv
    save_dir = '/home/j/temp/beatrixh/sim_science/outputs/WA_synthetic_pop_distribution/' + '_'.join(races)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    output.to_csv(save_dir + '/estimates_' + str(start) + '_' + str(stop) + '.csv', index = False)
    
    
if __name__=="__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("state", help="", type=str)
    parser.add_argument("races", help="comma-delimited string of acs race vars", type=str)
    parser.add_argument("start", help="to subset decennial df", type=int)
    parser.add_argument("stop", help="to subset decennial df", type=int)
    args = parser.parse_args()
    main(args.state, args.races, args.start, args.stop)