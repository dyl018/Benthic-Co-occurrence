#calculate benthic similarity
#Dylan Cowley: 03/02/2026

# prerequisite:
#   - 01_reclassify_field_data.py
#       - reclassified field data into key benthic mapping categories

# input:
#   - HR_benthic_data_adj.csv
#       - geolocated benthic data with geomorphic zones assigned (and manually adjusted)
#       - manual adjustments required for some points lying just outside
#         boundaries of geomorphic zones 

# output:
#   - benthic co-occurrence results

# %% (0) PACKAGE IMPORTS
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from alive_progress import alive_bar
import os

# %% (1) USER INPUTS
# --------------- (a) define analysis parameters ---------------
SITE = 'HR' # define site: HR = Heron Reef, EB = Eastern Banks
BENTHIC_TYPE = 'coral' # 'coral' or 'seagrass'
PIXEL_SIZES = [1, 2, 3.7, 5, 10, 18, 20, 30, 60, 76, 100, 300] # pixel sizes in meters
SELECTED_GZ = 'Reef_Slope_North' # specific geomorphic zone or 'all' for no filter
MIN_YR = 2007 # minimum year range for filtering
MAX_YR = 2025 # maximum year range for filtering
THRESHOLD = 0 # for filtering percent cover

# --------------- (b) define working directory ---------------
ROOT = r'C:\Users\uqdcowl2\OneDrive - The University of Queensland\Work PC\Documents\02_smartsat'
if SITE == 'HR':
    pwd = ROOT+r'\data\ReefCloud\HR_data\FieldData\04_output_reclassified'
elif SITE == 'EB':
    pwd = ROOT+r'\data\ReefCloud\EB_data'
OUTPUT_PATH = ROOT+r'output\benthic_cooccurrence'+'/'+BENTHIC_TYPE
df = pd.read_csv(os.path.join(pwd,SITE+'_benthic_adj.csv')) # read data

# %% (2) APPLY FILTERS
# --------------- (a) spatial filter ---------------
if SELECTED_GZ.lower() != "all":
    df = df[df['geomorphic_zone'] == SELECTED_GZ] # geomorphic zone
radii = [PIXEL_SIZES[i]/2 for i in range(len(PIXEL_SIZES))] # radius for filtering

# --------------- (b) temporal filter ---------------
df = df[df['year'] >= MIN_YR] 
df = df[df['year'] <= MAX_YR]
unique_dates = sorted(df['year_month'].unique()) # retrieve unique year/month combinations in the dataset

# --------------- (c) initialise storage ---------------
all_year_results = []

# %% (3) SIMILARITY ANALYSIS
with alive_bar(len(unique_dates)) as bar:
    for year_month in unique_dates: 
        # --------------- (a) data conversion ---------------
        df_year = df[df['year_month'] == year_month].reset_index(drop=True) # filter data for this year
        
        # reorganise columns
        id_vars = ['year', 'month', 'year_month', 'X', 'Y', 'geomorphic_zone']
        if SITE == 'HR':
            filter_mapping = pd.read_csv(os.path.join(pwd, 'labelmap_reefcloud.csv'),
                                                  low_memory=False)
            functional_group_cols = np.unique(filter_mapping.functional_group) # unique thematic groups
            fg_cols = [x for x in functional_group_cols if x != 'other']
        elif SITE == 'EB':
            functional_group_cols = ['Dense', 'Sparse', 'Algae', 'Lyngbya', 'Sand']
        
        # convert from wide format to long format
        df_long = pd.melt(
            df_year, 
            id_vars = id_vars,
            value_vars = fg_cols,
            var_name = 'functional_group',
            value_name = 'cover'
        )
        df_long = df_long[['year', 'month', 'year_month', 'X', 'Y', 'functional_group', 'cover', 'geomorphic_zone']]
        df_long['cover'] = df_long['cover']/100 # convert from percent to decimal
        df_long = df_long[df_long['cover'] > THRESHOLD] # remove cases with 0 cover
        
        # organise thematic groups by location (X, Y)
        grouped = df_long.groupby(['X', 'Y', 'geomorphic_zone'])['functional_group'].apply(list).reset_index()
        grouped = grouped.rename(columns={'functional_group': 'fg_list'})
        
        # get unique functional groups and re-sort
        all_groups = set()
        grouped['fg_list'].apply(lambda x: all_groups.update(x))
        groups_list = list(all_groups)
        other_groups = [g for g in groups_list if g.lower() == 'other']
        non_other_groups = [g for g in groups_list if g.lower() != 'other']
        all_groups = sorted(non_other_groups) + sorted(other_groups)
        group_index = {g: i for i, g in enumerate(all_groups)}
        
        # --------------- (b) construct coordinate arrays ---------------
        grouped = grouped.reset_index(drop=True)
        coords = grouped[['X', 'Y']].values
        gz_values = grouped['geomorphic_zone'].values
        fg_lists = grouped['fg_list'].values # functional group list
        
        # build spatial index tree
        tree = cKDTree(coords)
        
        # initialise results storage
        year_results = []
    
        # --------------- (c) analysis by pixel size ---------------
        for i, pixel_size in enumerate(PIXEL_SIZES):        
            radius = radii[i]
            
            # create presence/absence matrix for each point's neighbourhood
            neighbourhood_matrix = np.zeros((len(grouped), len(all_groups)), dtype=bool)
            neighbourhood_counts = np.zeros((len(grouped), len(all_groups)), dtype=int)
            
            for idx, row in grouped.iterrows():
                gz1 = row['geomorphic_zone']
                # find all points within radius (including self)
                indices = tree.query_ball_point(coords[idx], r=radius)
                
                # collect all thematic groups in this neighbourhood
                neighbourhood_groups = set()
                group_counter = {} # dictionary to count occurrences
                
                for nbr_idx in indices:
                    gz2 = grouped.at[nbr_idx, 'geomorphic_zone']
                    # only include neighbours from the same geomorphic zone
                    if gz1 == gz2:
                        nbr_groups = grouped.at[nbr_idx, 'fg_list']
                        neighbourhood_groups.update(nbr_groups)
                    
                        # count each group occurrence
                        for group in nbr_groups:
                            group_counter[group] = group_counter.get(group, 0)+1
                
                # mark presence of each thematic group in this neighbourhood
                for group in neighbourhood_groups:
                    group_idx = group_index[group]
                    neighbourhood_matrix[idx, group_idx] = True
                    neighbourhood_counts[idx, group_idx] = group_counter[group]
            
            total_occurrences = np.sum(neighbourhood_matrix, axis=0)
            
            # calculate Jaccard similarity between thematic groups
            n_groups = len(all_groups)
            jaccard_matrix = np.zeros((n_groups, n_groups), dtype=float)
            probability_matrix = np.zeros((len(neighbourhood_counts), n_groups), dtype=float)
            intersection_matrix = np.zeros((n_groups, n_groups), dtype=float)
            
            # determine presence/absence matrix
            for j in range(n_groups):
                for k in range(n_groups):
                    if j == k:
                        jaccard_matrix[j, k] = 1.0
                    else:
                        # get presence vectors for groups j and k across all neighbourhoods
                        presence_j = neighbourhood_matrix[:, j]
                        presence_k = neighbourhood_matrix[:, k]
                        
                        # calculate intersection and union
                        intersection = np.sum(presence_j & presence_k)
                        union = np.sum(presence_j | presence_k)
                        intersection_matrix[j, k] = intersection
                        
                        # account for no data or NaN cases
                        if union > 0:
                            jaccard_matrix[j, k] = intersection/union
                        else:
                            jaccard_matrix[j, k] = 0.0
            
            # determine probability matrix
            for j in range(n_groups):
                probability_matrix[:,j] = neighbourhood_counts[:,j]/neighbourhood_counts.sum(axis=1)
            
            # convert probability data into dataframe
            probability_df = pd.DataFrame(probability_matrix, columns = fg_cols)
            
            # store results for this pixel size
            for j, group1 in enumerate(all_groups):
                for k, group2 in enumerate(all_groups):
                    if j <= k: # only store upper triangle + diagonal to avoid duplicates
                        result_entry = {
                            'date': year_month,
                            'pixel_size_m': pixel_size,
                            'group1': group1,
                            'group2': group2,
                            'jaccard_similarity': jaccard_matrix[j, k],
                            'intersection': intersection_matrix[j ,k],
                            'count_group1': total_occurrences[j],
                            'count_group2': total_occurrences[k]
                        }
                        year_results.append(result_entry)
        print(f"{year_month} processed...")
        bar()
            
        # add year results to overall storage
        all_year_results.extend(year_results)
print('Complete!')
    
# %% (4) BASIC STATISTICS
results_df = pd.DataFrame(all_year_results)

# --------------- (a) annual mean and variance ---------------
avg_by_pixel_size = [] # similarity mean for each pixel size across all years
for pixel_size in PIXEL_SIZES:
    for year_month in unique_dates:
        year_pixel_data = results_df[
            (results_df['pixel_size_m'] == pixel_size) & 
            (results_df['date'] == year_month) &
            (results_df['group1'] != results_df['group2'])
        ]
        
        if len(year_pixel_data) > 0:
            avg_sim = year_pixel_data['jaccard_similarity'].mean()
            var_sim = year_pixel_data['jaccard_similarity'].var()
            yearly_entry = {
                'date': year_month,
                'pixel_size_m': pixel_size, 
                'avg_similarity': avg_sim,
                'var_similarity': var_sim
            }
            avg_by_pixel_size.append(yearly_entry)

avg_df = pd.DataFrame(avg_by_pixel_size)

# %% (5) SAVE DATA
# --------------- (a) export as .csv ---------------
# export annual mean and variance dataframe
avg_filename = f"{SELECTED_GZ}_summary.csv"
avg_df.to_csv(os.path.join(OUTPUT_PATH, avg_filename), index=False)

# export main results dataframe
results_filename = f"{SELECTED_GZ}_results.csv"
results_df.to_csv(os.path.join(OUTPUT_PATH, results_filename), index=False)