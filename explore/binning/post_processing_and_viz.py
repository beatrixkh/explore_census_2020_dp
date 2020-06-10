import pandas as pd, numpy as np

from process_acs import *
from process_decennial import *
from sample_data import *

import pyomo.environ
from pyomo.core import *
from pyomo.opt import SolverFactory

import matplotlib.pyplot as plt

def read_dir(race):
    in_dir = '/home/j/temp/beatrixh/sim_science/outputs/WA_synthetic_pop_distribution/'
    files = os.listdir(in_dir + race)
    
    df = pd.DataFrame()
    for file in files:
        sub_df = pd.read_csv(in_dir + race + '/' + file)
        df = df.append(sub_df)
    return df

def aggregate_by_age(input_df, count_var, how = 'a1'):
      
    # copy input df
    df = input_df.copy(deep=True)

    # create age map 
    age_map = pd.DataFrame(data = np.arange(0,121), columns=['age'])
    
    # create age_start col
    if how=='a1':
        age_map['a1_start'] = [i if i < 85 else (i - i%5) if i < 100 else 100 for i in age_map.age]
    elif how=='a2':
        age_map['a2_start'] = [i if i < 90 else (i- i%5) if i < 100 else 100 for i in age_map.age]
    elif how=='a3':
        age_map['a3_start'] = [i if i < 90 else 90 for i in age_map.age]

    # merge on age 
    df.age = df.age.astype(int)
    df = df.merge(age_map, on='age', how = 'left')
    
    # sum total counts by age groups
    a_total = how + '_total'
    a_start = how + '_start'
    df[a_total] = df.groupby([a_start, 'geoid', 'sex_id','race'])[count_var].transform('sum')
    
    # return df subset by new age groups
    return df[['geoid','race','sex_id',a_start,a_total]].drop_duplicates()

def das(input_df, counts_var, noise_parameter):
    """ takes in dataframe with a column, 'pop_count', with actual counts
        outputs dataframe with new columns for noisy and nonneg counts
    """
    df = input_df.copy(deep=True)
    
    n = df.shape[0]
    
    # add laplace noise 
    noise = np.random.laplace(loc=0, scale=noise_parameter, size=n)
    df['noisy_counts'] = df[counts_var] + noise
    
    # post processing
    df['nonneg_counts'] = post_proc(df.noisy_counts, df.pop_count.sum())
    df.nonneg_counts = np.round(df.nonneg_counts)
    
    return df

def post_proc(noisy_counts, control_total):
    """optimize the noisy counts so that they sum to
    the control total and are non-negative
    
    Parameters
    ----------
    noisy_counts : list-like of floats
    control_total : float
    
    Results
    -------
    returns optimized_counts, which are close to noisy counts,
    but not negative, and match control total in aggregate
    """
    noisy_counts = list(noisy_counts)
    
    model = ConcreteModel()
    model.I = range(len(noisy_counts))
    model.x = Var(model.I, within=NonNegativeReals)
    model.objective = Objective(
        expr=sum((model.x[i] - noisy_counts[i])**2 for i in model.I))
    model.constraint = Constraint(
        expr=summation(model.x) == control_total)
    
    solver = SolverFactory('ipopt')
    results = solver.solve(model, options={'acceptable_tol':1e-4}, tee=False)
    optimized_counts = [value(model.x[i]) for i in model.I]
        
    return np.array(optimized_counts)

def count_pop_leq(df, var, x):
    return df[df[var] <= x].shape[0]

def plot_small_vals(df, var = 'pop_count', label = 'pop_count', cutoffs = 1.2**np.arange(35)):
    leq_df = pd.DataFrame(columns = ['x'], data = cutoffs)
    leq_df['fx'] = [count_pop_leq(df, var, i) for i in leq_df.x]
    
    plt.scatter(x = leq_df.x, y = leq_df.fx, label = label)
    
#     plt.title('Count of rows with small values')
    plt.xlabel('Cutoff val')
    plt.ylabel('Count of rows leq cutoff val')
    
    plt.legend()