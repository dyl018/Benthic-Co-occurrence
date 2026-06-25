#benthic similarity plots
#Dylan Cowley: 25/06/2026

# prerequisite:
#   - 02_cooccurrence.py
#       - benthic similarity results 

# input:
#   - {geomorphic_zone}_summary.csv
#       - overall average and variance in cooccurrence across each geomorphic zone
#   - {geomorphic_zone}_results.csv
#       - all results from cooccurrence analysis

# output:
#   - benthic co-occurrence heatmaps and summary plots

# %% (0) PACKAGE IMPORTS
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from scipy import stats

# %% (1) USER INPUT
# --------------- (a) define plotting parameters ---------------
SITE = 'HR' # define site: HR = Heron Reef, EB = Eastern Banks
OPT = '' # for EB data: 'species' or 'dense'
BENTHIC_TYPE = 'coral' # 'coral' or 'seagrass'
plt.rcParams['legend.title_fontsize'] = 'medium'
plt.rcParams.update({'font.size': 16}) # font size
MIN_JS = 0 # max similarity for plotting
MAX_JS = 1 # min similarity for plotting

if SITE == 'HR':
    GZ_LIST = ['all', 'Reef_Flat_Inner', 'Reef_Flat_Outer', 'Reef_Slope_North',
               'Reef_Slope_South']
elif SITE == 'EB':
    GZ_LIST = ['all', 'Amity', 'Maroom', 'Moreton', 'WangaWallen']

SAVE_FIGURE = 'no' # yes or no

# --------------- (b) define working directory ---------------
ROOT = r'C:\Users\dcowl\OneDrive - The University of Queensland\Work PC\Documents\02_smartsat'
PWD = ROOT+r'\output\benthic_cooccurrence'+'/'+BENTHIC_TYPE
FIGPATH = ROOT+r'\figures\co-occurrence'+'/'+BENTHIC_TYPE

# %% (2) READ DATA
df_all = []
for selected_gz in GZ_LIST:
    # --------------- (a) read results ---------------
    df = pd.read_csv(os.path.join(PWD, selected_gz+'_results.csv')) # results
    if SITE == 'HR': # partial survey dates for removal
        df = df[df.date != 201609]
        df = df[df.date != 202403]
        df = df[df.date != 202405]
        df = df[df.date != 202408]
    
    # --------------- (b) read summary ---------------
    df_avg = pd.read_csv(os.path.join(PWD, selected_gz+'_summary.csv')) # summary results
    if SITE == 'HR': # partial survey dates for removal
        df_avg = df_avg[df_avg.date != 201609]
        df_avg = df_avg[df_avg.date != 202403]
        df_avg = df_avg[df_avg.date != 202405]
        df_avg = df_avg[df_avg.date != 202408]
    df_avg['geomorphic_zone'] = selected_gz # add geomorphic zone
    
    # --------------- (c) plotting information ---------------
    pixel_sizes = df['pixel_size_m'].unique()
    all_dates = pd.to_datetime(df_avg['date'], format='%Y%m').dt.strftime('%Y/%m').unique()
    all_dates = sorted(all_dates) # ensure chronological order is maintained
    
    # --------------- (d) append data ---------------
    df_all.append(df_avg)
    
    # %% (3) SUMMARY PLOTS
    # create main subplot layout
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    
    # --------------- (a) similarity average vs pixel size ---------------
    ax1 = axes[0, 0]
    ax1.fill_between(df_avg['pixel_size_m'].unique(), 
                     df_avg.groupby(['pixel_size_m'])['avg_similarity'].min(),
                     df_avg.groupby(['pixel_size_m'])['avg_similarity'].max(),
                     alpha=0.1, color='steelblue', label='Range')
    ax1.fill_between(df_avg['pixel_size_m'].unique(), 
                     df_avg.groupby(['pixel_size_m'])['avg_similarity'].quantile(0.25),
                     df_avg.groupby(['pixel_size_m'])['avg_similarity'].quantile(0.75),
                     alpha=0.3, color='steelblue', label='IQR')
    ax1.plot(df_avg['pixel_size_m'].unique(), df_avg.groupby(['pixel_size_m'])['avg_similarity'].mean(), 'o-', 
             linewidth=3, markersize=8, color='steelblue', label='Mean')
    ax1.set_xlabel('Pixel Size (m)')
    ax1.set_ylabel('Mean Jaccard Similarity')
    ax1.set_xlim([1, 300])
    ax1.set_ylim([0, 1])
    ax1.legend(title='Similarity Mean', loc='lower left')
    
    # --------------- (b) similarity variance vs pixel size ---------------
    ax2 = axes[0, 1]
    ax2.fill_between(df_avg['pixel_size_m'].unique(), 
                     df_avg.groupby(['pixel_size_m'])['var_similarity'].min(),
                     df_avg.groupby(['pixel_size_m'])['var_similarity'].max(),
                     alpha=0.1, color='coral', label='Range')
    ax2.fill_between(df_avg['pixel_size_m'].unique(), 
                     df_avg.groupby(['pixel_size_m'])['var_similarity'].quantile(0.25),
                     df_avg.groupby(['pixel_size_m'])['var_similarity'].quantile(0.75),
                     alpha=0.3, color='coral', label='IQR')
    ax2.plot(df_avg['pixel_size_m'].unique(), df_avg.groupby(['pixel_size_m'])['var_similarity'].mean(), 'o-', 
             linewidth=3, markersize=8, color='coral', label='Mean')
    ax2.set_xlabel('Pixel Size (m)')
    ax2.set_ylabel('Variance in Jaccard Similarity')
    ax2.set_xlim([1, 300])
    ax2.set_ylim([0, 0.2])
    ax2.legend(title='Similarity Variance', loc='upper right')
    
    # --------------- (c) temporal pixel comparison ---------------
    ax3 = axes[1, 0]
    colours = plt.cm.plasma(np.linspace(0, 1, len(pixel_sizes)))
    
    for i, ps in enumerate(pixel_sizes):
        pixel_data = df_avg[df_avg['pixel_size_m'] == ps]
        date_objects = pd.to_datetime(pixel_data['date'], format='%Y%m')
        ax3.plot(date_objects, pixel_data['avg_similarity'], 'o-', 
                linewidth=2, markersize=6, color=colours[i], label=f'{ps}')
    
    ax3.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())
    ax3.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Mean Jaccard Similarity')
    ax3.set_xlim([pd.to_datetime(2007, format='%Y'), pd.to_datetime(2026, format='%Y')])
    ax3.set_ylim([0, 1])
    ax3.legend(title='Pixel Size (m)', ncols=4, loc='lower left')

    # --------------- (d) pariwise similarities ---------------
    ax4 = axes[1, 1]
    
    # define functional group pairs and labels
    if SITE == 'HR':
        fg_pairs = [
            ('macroalgae', 'turf_cca'),
            ('macroalgae', 'hard_coral'),
            ('macroalgae', 'soft_coral'),
            ('macroalgae', 'sand'),
            ('turf_cca', 'hard_coral'),
            ('turf_cca', 'soft_coral'),
            ('turf_cca', 'sand'),
            ('hard_coral', 'soft_coral'),
            ('hard_coral', 'sand'),
            ('soft_coral', 'sand')
        ]
        fg_pair_labels = [
            'Macroalgae-Turf/Encrusting',
            'Macroalgae-Hard Coral',
            'Macroalgae-Soft Coral',
            'Macroalgae-Sand',
            'Turf/Encrusting-Hard Coral',
            'Turf/Encrusting-Soft Coral',
            'Turf/Encrusting-Sand',
            'Hard Coral-Soft Coral',
            'Hard Coral-Sand',
            'Soft Coral-Sand'
        ]
        # define colours for each thematic group
        fg_colours = {
            'hard_coral': '#FF91A4',
            'soft_coral': '#C41E3A',
            'sand': '#C19A6B',
            'macroalgae': '#6B8E23',
            'turf_cca': '#008B8B'
        }
    elif SITE == 'EB':
        if OPT == 'dense':
            fg_pairs = [
                ('Dense', 'Sparse'),
                ('Dense', 'Algae'),
                ('Dense', 'Lyngbya'),
                ('Dense', 'Sand'),
                ('Sparse', 'Algae'),
                ('Sparse', 'Lyngbya'),
                ('Sparse', 'Sand'),
                ('Algae', 'Lyngbya'),
                ('Algae', 'Sand'),
                ('Lyngbya', 'Sand')
            ]
            fg_pair_labels = [
                'Dense-Sparse',
                'Dense-Macroalgae',
                'Dense-Lyngbya',
                'Dense-Sand',
                'Sparse-Macroalgae',
                'Sparse-Lyngbya',
                'Sparse-Sand',
                'Macroalgae-Lyngbya',
                'Macroalgae-Sand',
                'Lyngbya-Sand'
            ]
            # define colours for each thematic group
            fg_colours = {
                'Dense': '#006937',
                'Sparse': '#75c376',
                'Algae': '#e7298a',
                'Lyngbya': '#000000',
                'Sand': '#fcf7c1'
            }
        elif OPT == 'species':
            fg_pairs = [
                ('Serrulata', 'Muelleri'),
                ('Serrulata', 'Uninervis'),
                ('Serrulata', 'Isoetifolium'),
                ('Serrulata', 'Spinulosa'),
                ('Serrulata', 'Ovalis'),
                ('Serrulata', 'Algae'),
                ('Serrulata', 'Lyngbya'),
                ('Serrulata', 'Sand'),
                ('Muelleri', 'Uninervis'),
                ('Muelleri', 'Isoetifolium'),
                ('Muelleri', 'Spinulosa'),
                ('Muelleri', 'Ovalis'),
                ('Muelleri', 'Algae'),
                ('Muelleri', 'Lyngbya'),
                ('Muelleri', 'Sand'),
                ('Uninervis', 'Isoetifolium'),
                ('Uninervis', 'Spinulosa'),
                ('Uninervis', 'Ovalis'),
                ('Uninervis', 'Algae'),
                ('Uninervis', 'Lyngbya'),
                ('Uninervis', 'Sand'),
                ('Isoetifolium', 'Spinulosa'),
                ('Isoetifolium', 'Ovalis'),
                ('Isoetifolium', 'Algae'),
                ('Isoetifolium', 'Lyngbya'),
                ('Isoetifolium', 'Sand'),
                ('Spinulosa', 'Ovalis'),
                ('Spinulosa', 'Algae'),
                ('Spinulosa', 'Lyngbya'),
                ('Spinulosa', 'Sand'),
                ('Ovalis', 'Algae'),
                ('Ovalis', 'Lyngbya'),
                ('Ovalis', 'Sand'),
                ('Algae', 'Lyngbya'),
                ('Algae', 'Sand'),
                ('Lyngbya', 'Sand'),
            ]
            fg_pair_labels = [
                'O. serrulata-Z. muelleri',
                'O. serrulata-H. uninervis',
                'O. serrulata-S. isoetifolium',
                'O. serrulata-H. spinulosa',
                'O. serrulata-H. ovalis',
                'O. serrulata-Macroalgae',
                'O. serrulata-Lyngbya',
                'O. serrulata-Sand',
                'Z. muelleri-H. uninervis',
                'Z. muelleri-S. isoetifolium',
                'Z. muelleri-H. spinulosa',
                'Z. muelleri-H. ovalis',
                'Z. muelleri-Macroalgae',
                'Z. muelleri-Lyngbya',
                'Z. muelleri-Sand',
                'H. uninervis-S. isoetifolium',
                'H. uninervis-H. spinulosa',
                'H. uninervis-H. ovalis',
                'H. uninervis-Macroalgae',
                'H. uninervis-Lyngbya',
                'H. uninervis-Sand',
                'S. isoetifolium-H. spinulosa',
                'S. isoetifolium-H. ovalis',
                'S. isoetifolium-Macroalgae',
                'S. isoetifolium-Lyngbya',
                'S. isoetifolium-Sand',
                'H. spinulosa-H. ovalis',
                'H. spinulosa-Macroalgae',
                'H. spinulosa-Lyngbya',
                'H. spinulosa-Sand',
                'H. ovalis-Macroalgae',
                'H. ovalis-Lyngbya',
                'H. ovalis-Sand',
                'Macroalgae-Lyngbya',
                'Macroalgae-Sand',
                'Lyngbya-Sand',
            ]
            # define colours for each thematic group
            fg_colours = {
                'Serrulata': '#006937',
                'Muelleri': '#248b45',
                'Uninervis': '#75c376',
                'Isoetifolium': '#c8e4bf',
                'Spinulosa': '#2272b5',
                'Ovalis': '#9ecae1',
                'Algae': '#e7298a',
                'Lyngbya': '#000000',
                'Sand': '#fcf7c1'
            }
    
    # plot each pair
    for i, pair in enumerate(fg_pairs):
        # filter for this specific pair
        pair_data = df[
            ((df['group1'] == pair[0]) & (df['group2'] == pair[1])) |
            ((df['group1'] == pair[1]) & (df['group2'] == pair[0]))
        ]
        
        if len(pair_data) > 0:
            # group by pixel size and calculate mean and std
            pixel_stats = pair_data.groupby('pixel_size_m')['jaccard_similarity'].agg(['mean', 'std'])
            
            pixel_sizes = pixel_stats.index.values
            mean_similarity = pixel_stats['mean'].values
            std_similarity = pixel_stats['std'].values
            
            colour = fg_colours[pair[0]]
            
            # plot mean line
            ax4.plot(pixel_sizes, mean_similarity, 'o-', 
                    linewidth=3, markersize=8, color=colour, 
                    label=f"{fg_pair_labels[i]}")
    
    ax4.set_xlabel('Pixel Size (m)')
    ax4.set_ylabel('Mean Jaccard Similarity')
    ax4.set_xlim([1, 300])
    ax4.set_ylim([MIN_JS, MAX_JS])
    ax4.legend(title='Functional Group Pairs', ncols=2, loc='best', fontsize=14)
    ax4.grid(alpha=0.3)
    
    # --------------- (e) figure export ---------------
    if SAVE_FIGURE == 'yes':
        name = f'{selected_gz}_summary.png'
        full_path = os.path.join(FIGPATH, name)
        plt.savefig(full_path, dpi=600)
    
    plt.show()
    
    # %% (4) THEMATIC GROUP HEATMAP
    # --------------- (a) thematic groups and figure layout ---------------
    #fg_list = sorted(set(df['group1'].unique()))
    if SITE == 'HR':
        fg_label_list = ['Macroalgae', 'Turf/Encrusting', 'Hard Coral', 'Sand', 'Soft Coral']
        fg_list = ['macroalgae', 'turf_cca', 'hard_coral', 'sand', 'soft_coral']
    elif SITE == 'EB':
        if OPT == 'dense':
            fg_label_list = ['Dense', 'Sparse', 'Macroalgae', 'Lyngbya', 'Sand']
            fg_list = ['Dense', 'Sparse', 'Algae', 'Lyngbya', 'Sand']
        elif OPT == 'species':
            fg_label_list = ['O. serrulata', 'Z. muelleri', 'H. uninervis', 
                             'S. isoetifolium', 'H. spinulosa', 'H. ovalis',
                             'Macrolgae', 'Lyngbya', 'Sand']
            fg_list = ['Serrulata', 'Muelleri', 'Uninervis', 'Isoetifolium', 
                       'Spinulosa', 'Ovalis', 'Algae', 'Lyngbya', 'Sand']
    n_groups = len(fg_list)
    
    # calculate number of plots and grid dimensions
    n_plots = len(pixel_sizes)
    n_cols = min(3, n_plots)
    n_rows = (n_plots+n_cols-1)//n_cols
    
    # --------------- (b) create heatmaps ---------------
    figsize_per_plot = (4, 3)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize_per_plot[0]*n_cols, figsize_per_plot[1]*n_rows),
                             gridspec_kw={'hspace': 0.02, 'wspace': 0.02})
        
    # process each pixel size
    for idx, ps in enumerate(pixel_sizes):
        row = idx//n_cols
        col = idx%n_cols
        ax = axes[row, col]
        
        # filter data for this pixel size and average over time
        pixel_data = df[df['pixel_size_m'] == ps].copy()
        
        # average similarity across years for each group pair
        avg_similarity = pixel_data.groupby(['group1', 'group2'])['jaccard_similarity'].mean().reset_index()
        
        # create similarity matrix
        similarity_matrix = np.zeros((n_groups, n_groups))
        
        for _, row_data in avg_similarity.iterrows():
            group1 = row_data['group1']
            group2 = row_data['group2']
            similarity = row_data['jaccard_similarity']
            
            # find indices
            idx1 = fg_list.index(group1)
            idx2 = fg_list.index(group2)
            
            # fill both positions
            similarity_matrix[idx1, idx2] = similarity
            similarity_matrix[idx2, idx1] = similarity
        
        # create upper triangular mask excluding diagonal
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool), k=1)
        
        # create masked matrix for plotting and set lower triangle and diagonal to NaN
        masked_matrix = similarity_matrix.copy()
        masked_matrix[~mask] = np.nan
        
        # create heatmap
        im = ax.imshow(masked_matrix, cmap='RdBu_r', aspect='auto', 
                      vmin=MIN_JS, vmax=MAX_JS, interpolation='nearest')
        last_im = im
        
        # set ticks for all subplots
        ax.set_xticks(range(n_groups))
        ax.set_yticks(range(n_groups))
        
        # determine if this subplot should show labels
        show_x_labels = (row == n_rows-1) # bottom row
        show_y_labels = (col == 0) # leftmost column
        
        # set labels only for appropriate subplots
        if show_x_labels:
            ax.set_xticklabels(fg_label_list, rotation=45, ha='right', fontweight='bold')
        else:
            ax.set_xticklabels([])
            
        if show_y_labels:
            ax.set_yticklabels(fg_label_list, fontweight='bold')
        else:
            ax.set_yticklabels([])
        
        # add text annotations for upper triangle (excluding diagonal)
        if SITE == 'HR':
            fs = 15
        else:
            fs = 9
        for i in range(n_groups):
            for j in range(i+1, n_groups): # only upper triangle, excluding diagonal
                if not np.isnan(masked_matrix[i, j]):
                    text_color = 'white' if masked_matrix[i, j] < 0.1 or masked_matrix[i, j] > 0.9 else 'black'
                    ax.text(j, i, f'{masked_matrix[i, j]:.2f}',
                           ha="center", va="center", color=text_color, fontsize=fs)
        
        # add pixel size title in the lower triangle area
        title_x = n_groups*0.2 # 20% from left
        title_y = n_groups*0.7 # 70% from top
        ax.text(title_x, title_y, f'{ps} m', fontsize=20,
               ha="center", va="center", fontweight='bold')
        
        if ps == 1:
            ax.text(title_x, title_y-0.7, 'Pixel Size', fontsize=18,
                    ha="center", va="center")
    
    # hide unused subplots
    for idx in range(n_plots, n_rows*n_cols):
        row = idx//n_cols
        col = idx%n_cols
        axes[row, col].set_visible(False)
        
    # add a colourbar
    fig.subplots_adjust(right=0.88)
    cbar_ax = fig.add_axes([0.92, 0.05, 0.03, 0.85]) # [left, bottom, width, height]
    cbar = fig.colorbar(last_im, cax=cbar_ax)
    cbar.set_label('Jaccard Similarity', fontsize=24, fontweight='bold')
    cbar.ax.tick_params(labelsize=20)
    
    # for transparency of background
    #fig.patch.set_alpha(0.0)
    #ax.patch.set_facecolor('white')
    #ax.patch.set_alpha(1.0)
    
    # broader axis labels
    #fig.text(0.5, -0.05, 'Benthic Group', ha='center', va='bottom', fontsize=24, fontweight='bold') # x-axis
    #fig.text(-0.06, 0.5, 'Benthic Group', ha='left', va='center', fontsize=24, fontweight='bold', rotation='vertical') # y-axis
    plt.tight_layout()
    
    # --------------- (c) figure export ---------------
    if SAVE_FIGURE == 'yes':
        name = f'{selected_gz}_heatmaps_transparent.png'
        full_path = os.path.join(FIGPATH, name)
        plt.savefig(full_path, dpi=600, bbox_inches='tight')
    
    plt.show()
    
    # %% (5) TEMPORAL HEATMAPS
    # --------------- (a) similarity mean ---------------
    fig, ax = plt.subplots(1, 1, figsize=(13, 10))
    
    # structure data for heatmap
    pivot_avg = df_avg.pivot(index='date', columns='pixel_size_m', values='avg_similarity')
    
    # create heatmap
    heatmap_avg = sns.heatmap(pivot_avg, annot=True, fmt='.2f', cmap='RdBu_r', 
               ax=ax, square=False, linewidths=0.5,
               vmin=MIN_JS, vmax=MAX_JS, annot_kws={'size': 18},
               cbar=False)
    ax.set_yticklabels(all_dates)
    ax.set_xlabel('Pixel Size (m)', fontweight='bold', fontsize=24)
    ax.set_ylabel('Survey Date (YYYY/MM)', fontweight='bold', fontsize=24)
    ax.tick_params(axis='x', rotation=45, labelsize=20)
    ax.tick_params(axis='y', rotation=0, labelsize=20)
    
    # add a colourbar
    fig.subplots_adjust(right=0.88)
    cbar_ax = fig.add_axes([0.92, 0.05, 0.03, 0.85])  # [left, bottom, width, height]
    cbar = fig.colorbar(heatmap_avg.collections[0], cax=cbar_ax)
    cbar.set_label('Jaccard Similarity Mean', fontsize=24, fontweight='bold')
    cbar.ax.tick_params(labelsize=20)
    
    # --------------- (b) figure export ---------------
    if SAVE_FIGURE == 'yes':
        name = f'{selected_gz}_temporal_overview.png'
        full_path = os.path.join(FIGPATH, name)
        plt.savefig(full_path, dpi=600, bbox_inches='tight')
    
    plt.show()

# %% (6) SIMILARITY VARIABILITY
# --------------- (a) plotting setup --------------- 
df_combined = pd.concat(df_all, ignore_index=True)

# define colour palette
if SITE == 'HR':
    zone_colours = {
        "all": "#808080",                  
        "Reef_Flat_Inner": "#B50609",
        "Reef_Flat_Outer": "#FC8D59",     
        "Reef_Slope_South": "#4575B4",
        "Reef_Slope_North": "#C7EBFF"   
        }
    legend_labels = {
        "all": "All zones",
        "Reef_Flat_Inner": "Reef Flat Inner",
        "Reef_Flat_Outer": "Reef Flat Outer",
        "Reef_Slope_South": "Reef Slope South",
        "Reef_Slope_North": "Reef Slope North"
    }
elif SITE == 'EB':
    zone_colours = {
        "all": "#808080",                  
        "Amity": "#D7191C",
        "Maroom": "#1A9641",     
        "Moreton": "#5E3C99",
        "WangaWallen": "#2B83BA"
        }

# --------------- (b) variability plots ---------------
fig, ax = plt.subplots(figsize=(14, 8))

extra_tick_pos = [5, 10, 20, 30] # positions to add some extra tick labels

for i in extra_tick_pos:
    plt.axvline(x=i, color='#828282', linestyle='--', dashes=(5, 5), linewidth=1, 
                alpha=0.5, label='_vline at x={i}')

for zone in GZ_LIST:
    if zone == 'all':
        linestyle = 'o:'
    else:
        linestyle = 'o-'
    df_zone = df_combined[df_combined['geomorphic_zone'] == zone].copy()
    ax.plot(pixel_sizes, df_zone.groupby('pixel_size_m')['avg_similarity'].mean(),
                 linestyle, linewidth=3, markersize=8, color=zone_colours[zone],
                 label=legend_labels[zone])
    
ax.set_ylabel('Jaccard Similarity Mean', fontsize=24, fontweight='bold')
ax.set_xlabel('Pixel Size (m)', fontsize=24, fontweight='bold')
#ax.set_xscale('log')
ax.set_ylim([MIN_JS, MAX_JS])
ax.set_xlim([1, 300])
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)

all_tick_positions = sorted(list(set(list(np.arange(0,301,50))+extra_tick_pos)))

ax.set_xticks(all_tick_positions)
for i, tick_label in enumerate(ax.get_xticklabels()):
    tick_line = ax.get_xticklines()[i]
    if all_tick_positions[i] in extra_tick_pos:
        # set colour for the extra ticks and labels
        tick_label.set_fontsize(16)
        tick_label.set_color('#828282')
        tick_line.set_color('#828282')

ax.tick_params(axis='both')
ax.legend(fontsize=20)

fig.patch.set_alpha(0.0)
ax.patch.set_facecolor('white')
ax.patch.set_alpha(1.0)

plt.tight_layout()

# --------------- (c) figure export ---------------
if SAVE_FIGURE == 'yes':
    name = 'similarity_overview_transparent.png'
    full_path = os.path.join(FIGPATH, name)
    plt.savefig(full_path, dpi=600)

plt.show()

# %% (7) PROBABILITY DENSITY FUNCTIONS BY CLASS PAIRS
# read the original results data that has group pairs
df_results = pd.read_csv(os.path.join(PWD, 'all_results.csv'))
if SITE == 'HR':
    df_results = df_results[df_results.date != 201609]
    fig, axes = plt.subplots(4, 3, figsize=(18, 20), gridspec_kw={'hspace': 0.05, 'wspace': 0.05})
elif SITE == 'EB':
    if OPT == 'species':
        fig, axes = plt.subplots(6, 6, figsize=(18, 20), gridspec_kw={'hspace': 0.05, 'wspace': 0.05})
    else:
        fig, axes = plt.subplots(4, 3, figsize=(18, 20), gridspec_kw={'hspace': 0.05, 'wspace': 0.05})
axes = axes.flatten()

# store all handles and labels for combined legend
all_handles = []
all_labels = []

# --------------- (a) PDF setup ---------------
for pair_idx, (group1, group2) in enumerate(fg_pairs):
    ax = axes[pair_idx]
    
    # filter data for this class pair
    df_pair = df_results[
        ((df_results['group1'] == group1) & (df_results['group2'] == group2)) |
        ((df_results['group1'] == group2) & (df_results['group2'] == group1))
    ].copy()
    
    # get unique pixel sizes and sort them
    pixel_sizes_sorted = sorted(df_pair['pixel_size_m'].unique())
    
    # create colour palette for pixel sizes
    colours = plt.cm.PuOr(np.linspace(0, 1, len(pixel_sizes_sorted)))
    
    # --------------- (b) calculate and plot PDFs ---------------
    # create x-axis values for smooth PDF curves
    x_pdf = np.linspace(0, 1, 200)
    
    for i, ps in enumerate(pixel_sizes_sorted):
        # get similarity data for this pixel size
        ps_data = df_pair[df_pair['pixel_size_m'] == ps]['jaccard_similarity'].dropna()
        
        # calculate kernel density estimation
        kde = stats.gaussian_kde(ps_data)
        pdf_values = kde(x_pdf)
        
        # plot PDF
        line, = ax.plot(x_pdf, pdf_values, linewidth=2.5, 
               color=colours[i], label=f'{int(ps)}', alpha=0.8)
        
        # collect handles and labels from first subplot only
        if pair_idx == 0:
            all_handles.append(line)
            all_labels.append(f'{int(ps)}')
        
        # add shaded area under curve
        ax.fill_between(x_pdf, pdf_values, alpha=0.15, color=colours[i])
    
    # --------------- (c) formatting ---------------
    # determine row and column position
    row = pair_idx//3
    col = pair_idx%3
    
    # only add x-label and ticks to bottom row
    if row == 3:
        ax.set_xlabel('Jaccard Similarity', fontweight='bold')
    elif row == 2 and (col == 1 or col == 2):
        ax.set_xlabel('Jaccard Similarity', fontweight='bold')
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', which='both', bottom=False)
    
    # only add y-label and ticks to left column
    if col == 0:
        ax.set_ylabel('Probability Density', fontweight='bold')
    else:
        ax.set_yticklabels([])
        ax.tick_params(axis='y', which='both', left=False)
    
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 10])
    
    # add title as text inside the plot
    ax.text(0.05, 0.95, fg_pair_labels[pair_idx], 
            transform=ax.transAxes, fontweight='bold', fontsize=20,
            verticalalignment='top')
    
    ax.grid(True, alpha=0.3, linestyle='--')

legend_ax = axes[10] # use the 11th subplot for the legend
legend_ax.axis('off')

# create legend in the 11th subplot
legend_ax.legend(all_handles, all_labels, title='Pixel Size (m)', 
                loc='lower center', ncol=2, fontsize=20, 
                frameon=True, title_fontproperties={'weight': 'bold', 'size': 22})

# hide the 12th subplot
axes[11].axis('off')

plt.tight_layout()

# --------------- (d) figure export ---------------
if SAVE_FIGURE == 'yes':
    name = 'all_pairs_similarity_pdf_4x3.png'
    full_path = os.path.join(FIGPATH, name)
    plt.savefig(full_path, dpi=600, bbox_inches='tight')

plt.show()

# %% (8) COMBINED PDF FOR ALL DATA
fig, ax = plt.subplots(figsize=(12, 8))

# get all unique pixel sizes and sort them
pixel_sizes_sorted = sorted(df_results['pixel_size_m'].unique())

# create colour palette for pixel sizes
colours = plt.cm.PuOr(np.linspace(0, 1, len(pixel_sizes_sorted)))

# create x-axis values for smooth PDF curves
x_pdf = np.linspace(0, 1, 200)

# calculate and plot PDFs for each pixel size across all class pairs
for i, ps in enumerate(pixel_sizes_sorted):
    # get all similarity data for this pixel size (across all class pairs)
    ps_data = df_results[df_results['pixel_size_m'] == ps]['jaccard_similarity'].dropna()
    
    # calculate kernel density estimation
    kde = stats.gaussian_kde(ps_data)
    pdf_values = kde(x_pdf)
    
    # plot PDF
    ax.plot(x_pdf, pdf_values, linewidth=3, 
           color=colours[i], label=f'{int(ps)} m', alpha=0.85)
    
    # add shaded area under curve
    ax.fill_between(x_pdf, pdf_values, alpha=0.2, color=colours[i])

# formatting
ax.set_xlabel('Jaccard Similarity', fontweight='bold', fontsize=16)
ax.set_ylabel('Probability Density', fontweight='bold', fontsize=16)
ax.set_xlim([0, 1])
ax.set_ylim([0, 10])
ax.set_ylim(bottom=0)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(title='Pixel Size (m)', loc='upper left', fontsize=14, 
          frameon=True, title_fontproperties={'weight': 'bold', 'size': 16})

plt.tight_layout()

# figure export
if SAVE_FIGURE == 'yes':
    name = f'combined_all_data_similarity_pdf_{SITE}.png'
    full_path = os.path.join(FIGPATH, name)
    plt.savefig(full_path, dpi=600, bbox_inches='tight')

plt.show()

# %% (9) REGRESSION
# --------------- (a) create figure with subplots ---------------
n_groups = len(fg_list)
fig, axes = plt.subplots(n_groups, n_groups, figsize=(20, 20),
                        gridspec_kw={'hspace': 0.15, 'wspace': 0.05}) # 5x5 grid

# create mapping from pairs to matrix position
pair_positions = {}
pair_idx = 0
for i in range(n_groups):
    for j in range(i+1, n_groups): # upper triangle only
        pair_positions[pair_idx] = (i, j)
        pair_idx += 1

# get unique pixel sizes
pixel_sizes_sorted = sorted(df_results['pixel_size_m'].unique())

similarity_stats_list = []

# --------------- (b) plot each thematic group pair ---------------
for pair_idx, pair in enumerate(fg_pairs):
    i, j = pair_positions[pair_idx] # get matrix position for this pair
    ax = axes[i, j] # assign correct axes
    
    pair_data = df_results[
        ((df_results['group1'] == pair[0]) & (df_results['group2'] == pair[1])) |
        ((df_results['group1'] == pair[1]) & (df_results['group2'] == pair[0]))
    ].copy() # filter for the right pair
    
    # calculate statistics grouped by both pixel_size_m and year
    pixel_year_stats = pair_data.groupby(['pixel_size_m', 'date'])['jaccard_similarity'].agg([
        'mean',
        lambda x: np.percentile(x, 25),
        lambda x: np.percentile(x, 75)
    ]).reset_index()
    pixel_year_stats.columns = ['pixel_size_m', 'date', 'mean', 'p25', 'p75']
    
    # add pair information
    pixel_year_stats['group1'] = pair[0]
    pixel_year_stats['group2'] = pair[1]
    pixel_year_stats['pair_label'] = fg_pair_labels[pair_idx]
    
    # append to list
    similarity_stats_list.append(pixel_year_stats)
    
    # aggregate across years for plotting
    pixel_stats = pair_data.groupby('pixel_size_m')['jaccard_similarity'].agg([
        'mean',
        lambda x: np.percentile(x, 25),
        lambda x: np.percentile(x, 75)
    ]).reset_index()
    pixel_stats.columns = ['pixel_size_m', 'mean', 'p25', 'p75']
    
    pixel_sizes_arr = pixel_stats['pixel_size_m'].values
    mean_similarity = pixel_stats['mean'].values
    p25 = pixel_stats['p25'].values # 25th percentile
    p75 = pixel_stats['p75'].values # 75th percentile
    
    colour = fg_colours[pair[0]] # retrieve colours
    ax.fill_between(pixel_sizes_arr, p25, p75,
                   alpha=0.2, color='#828282', edgecolor=None) # patch for IQR
    
    # plot mean line with markers
    ax.plot(pixel_sizes_arr, mean_similarity, '-', 
           linewidth=1.5, color=fg_colours[pair[1]])
    ax.plot(pixel_sizes_arr, mean_similarity, 'o--', dashes=(5, 5), 
           linewidth=2.5, markersize=7, color=colour)

    # log scale data
    ps_log = np.log(pixel_sizes_arr)
    ym = np.log(mean_similarity)
    
    L_list = np.arange(-10,10,10/100) # tries for L
    k_list = np.arange(-1,1,1/100) # tries for k
    
    r2_mc = np.zeros((len(L_list),len(k_list)))
    for mcL in range(0,len(L_list)):
        for mcK in range(0, len(k_list)):
            L = L_list[mcL]
            k = k_list[mcK]
            ym_fit = -(L/(1+np.exp((k*ps_log)-1))) # logistic fit
            ssres = np.sum(np.square(ym_fit-ym))
            sstot = np.sum(np.square(ym_fit-np.mean(ym_fit)))
            r2_mc[mcL, mcK] = 1-(ssres/sstot)
    
    # find optimal fit
    max_idx = np.argmax(r2_mc)
    row, col = np.unravel_index(max_idx, r2_mc.shape)
    
    # plot the logarithmic fit as a dashed line
    x_fit = np.linspace(pixel_sizes_arr.min(), pixel_sizes_arr.max(), 100)
    y_fit = np.exp(-(L_list[row]/(1+np.exp(k_list[col]*np.log(x_fit)-1))))
    ax.plot(x_fit, y_fit, '--', linewidth=2, color='black', alpha=0.6)
    
    # add equation and R2 to plot with title
    #eq_text = f'{fg_pair_labels[pair_idx]}\n$L = ${L_list[row]:.1f}, $k = ${k_list[col]:.2f}\n$R^2 = ${r2_mc[row, col]:.3f}'
    #ax.text(0.1, 0.25, eq_text, transform=ax.transAxes,
    #       fontsize=10, verticalalignment='top',
    #       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # x-label and ticks to leading diagonal
    if j == i+1:
        ax.set_xlabel('Pixel Size (m)', fontweight='bold', fontsize=18)
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', which='both', bottom=True, labelbottom=False, labelsize=16)
    
    # y-label and ticks to leading diagonal
    if j == i+1:
        ax.set_ylabel('Mean Similarity', fontweight='bold', fontsize=18)
    else:
        ax.set_yticklabels([])
        ax.tick_params(axis='y', which='both', left=True, labelleft=False, labelsize=16)
    
    # formatting for each subplot
    ax.set_xlim([1, 100])
    ax.set_ylim([0, 1])
    ax.grid(alpha=0.3, linestyle='--')

# combine all statistics into a single dataframe
df_similarity_stats = pd.concat(similarity_stats_list, ignore_index=True)

# reorder columns for clarity
df_similarity_stats = df_similarity_stats[['group1', 'group2', 'pair_label', 
                                           'pixel_size_m', 'date', 
                                           'mean', 'p25', 'p75']]

# sort by pair, pixel size, and year
df_similarity_stats = df_similarity_stats.sort_values(['pair_label', 'pixel_size_m', 'date']).reset_index(drop=True)

# hide diagonal and lower triangle
for i in range(n_groups):
    for j in range(i+1): # diagonal and lower triangle
        axes[i, j].set_visible(False)

plt.tight_layout()

# --------------- (c) figure export ---------------
if SAVE_FIGURE == 'yes':
    name = f'pairwise_similarity_{SITE}_nolabs.png'
    full_path = os.path.join(FIGPATH, name)
    plt.savefig(full_path, dpi=600, bbox_inches='tight')

plt.show()

# %% (10) SEGMENTED REGRESSION ANALYSIS
# initialise list to store segmented regression results
segmented_results_list = []

# --------------- (a) perform segmented regression for each pair ---------------
for pair_idx, pair in enumerate(fg_pairs):   
    # filter data for this pair
    pair_data = df_results[
        ((df_results['group1'] == pair[0]) & (df_results['group2'] == pair[1])) |
        ((df_results['group1'] == pair[1]) & (df_results['group2'] == pair[0]))
    ].copy()
    
    # calculate mean similarity for each pixel size
    pixel_stats = pair_data.groupby('pixel_size_m')['jaccard_similarity'].mean().reset_index()
    pixel_stats.columns = ['pixel_size_m', 'mean_similarity']
    
    x = pixel_stats['pixel_size_m'].values
    y = pixel_stats['mean_similarity'].values
    
    # sort by pixel size
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]
    
    # try different breakpoints
    n_points = len(x)
    best_r2 = -np.inf # placeholder
    best_breakpoint = None
    best_params = None
    
    # store results for each breakpoint attempt
    breakpoint_results = []
    
    for bp_idx in range(2, n_points-2): # iterate through potential breakpoints
        break_point = x[bp_idx]
        
        # split data at breakpoint
        left_mask = x <= break_point
        right_mask = x > break_point
        
        x_left = x[left_mask]
        y_left = y[left_mask]
        x_right = x[right_mask]
        y_right = y[right_mask]
        
        # fit linear regression on left segment
        if len(x_left) >= 2:
            coeffs_left = np.polyfit(x_left, y_left, 1)
            a1, b1 = coeffs_left[0], coeffs_left[1]
            y_pred_left = a1*x_left+b1
        else:
            continue
        
        # fit linear regression on right segment
        if len(x_right) >= 2:
            coeffs_right = np.polyfit(x_right, y_right, 1)
            a2, b2 = coeffs_right[0], coeffs_right[1]
            y_pred_right = a2*x_right+b2
        else:
            continue
        
        # calculate overall R2 for segmented model
        y_pred = np.concatenate([y_pred_left, y_pred_right])
        ss_res = np.sum((y-y_pred)**2)
        ss_tot = np.sum((y-np.mean(y))**2)
        r2 = 1-(ss_res/ss_tot)
        
        # calculate individual R2 for each segment
        ss_res_left = np.sum((y_left-y_pred_left)**2)
        ss_tot_left = np.sum((y_left-np.mean(y_left))**2)
        r2_left = 1-(ss_res_left/ss_tot_left) if ss_tot_left > 0 else 0
        
        ss_res_right = np.sum((y_right-y_pred_right)**2)
        ss_tot_right = np.sum((y_right-np.mean(y_right))**2)
        r2_right = 1-(ss_res_right/ss_tot_right) if ss_tot_right > 0 else 0
        
        # store results
        breakpoint_results.append({
            'breakpoint': break_point,
            'r2_overall': r2,
            'r2_left': r2_left,
            'r2_right': r2_right,
            'a1': a1, 'b1': b1,
            'a2': a2, 'b2': b2,
            'n_left': len(x_left),
            'n_right': len(x_right)
        })
        
        # update best model
        if r2 > best_r2:
            best_r2 = r2
            best_breakpoint = break_point
            best_params = {
                'a1': a1, 'b1': b1,
                'a2': a2, 'b2': b2,
                'r2_left': r2_left,
                'r2_right': r2_right,
                'n_left': len(x_left),
                'n_right': len(x_right)
            }
    
    # store results for this pair
    result = {
        'group1': pair[0],
        'group2': pair[1],
        'pair_label': fg_pair_labels[pair_idx],
        'breakpoint': best_breakpoint,
        'r2_piecewise': best_r2,
        'slope_left': best_params['a1'],
        'intercept_left': best_params['b1'],
        'slope_right': best_params['a2'],
        'intercept_right': best_params['b2'],
        'r2_left': best_params['r2_left'],
        'r2_right': best_params['r2_right'],
        'n_points_left': best_params['n_left'],
        'n_points_right': best_params['n_right']
    }
    
    segmented_results_list.append(result)

df_piecewise = pd.DataFrame(segmented_results_list)

# --------------- (b) visualise fits ---------------
# create a figure showing the best segmented fits
n_pairs = len(fg_pairs)
n_cols = 3
n_rows = int(np.ceil(n_pairs/n_cols))

fig_pw, axes = plt.subplots(n_groups, n_groups, figsize=(20, 20),
                        gridspec_kw={'hspace': 0.15, 'wspace': 0.05}) # 5x5 grid

for pair_idx, pair in enumerate(fg_pairs):
    i, j = pair_positions[pair_idx] # get matrix position for this pair
    ax = axes[i, j] # assign correct axes
    
    # get data for this pair
    pair_data = df_results[
        ((df_results['group1'] == pair[0]) & (df_results['group2'] == pair[1])) |
        ((df_results['group1'] == pair[1]) & (df_results['group2'] == pair[0]))
    ].copy()
    
    pixel_stats = pair_data.groupby('pixel_size_m')['jaccard_similarity'].mean().reset_index()
    x = pixel_stats['pixel_size_m'].values
    y = pixel_stats['jaccard_similarity'].values
    
    # sort by pixel size
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]
    
    # get segmented regression parameters
    pw_result = df_piecewise[df_piecewise['pair_label'] == fg_pair_labels[pair_idx]].iloc[0]
    break_point = pw_result['breakpoint']
    a1, b1 = pw_result['slope_left'], pw_result['intercept_left']
    a2, b2 = pw_result['slope_right'], pw_result['intercept_right']
    
    # p breakpoint
    y_at_breakpoint = a1*break_point+b1
    ax.axvline(break_point, color='black', linestyle='--', dashes = (3, 3), linewidth=2, 
                  alpha=0.6, label=f'Breakpoint: {breakpoint:.1f}m', zorder=1)
    
    # plot segmented regression
    x_left = x[x <= break_point]
    x_right = x[x > break_point]
    y_left_fit = a1*x_left+b1
    y_right_fit = a2*x_right+b2
    
    ax.plot(x_left, y_left_fit, '-', linewidth=2, color='red', 
               label='Left Fit')
    ax.plot(x_right, y_right_fit, '-', linewidth=2, color='blue', 
               label='Right Fit')
    
    # plot data points
    ax.scatter(x, y, s=80, alpha=0.6, color='black', 
                  edgecolors=None, label='Data')
    
    # fitting stats
    #ax.text(0.3, 0.5, f'{fg_pair_labels[pair_idx]}\n$R^2 = ${pw_result["r2_piecewise"]:.4f}',
    #        transform=ax.transAxes, fontsize=10, verticalalignment='top',
    #        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # x-label and ticks to leading diagonal
    if j == i+1:
        if SITE == 'HR':
            ax.set_xlabel('Pixel Size (m)', fontweight='bold', fontsize=18)
        else:
            ax.set_xlabel('PS (m)', fontweight='bold', fontsize=18)
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', which='both', bottom=True, labelbottom=False, labelsize=16)
    
    # y-label and ticks to leading diagonal
    if j == i+1:
        if SITE == 'HR':
            ax.set_ylabel('Mean Similarity', fontweight='bold', fontsize=18)
        else:
            ax.set_ylabel('Jaccard', fontweight='bold', fontsize=18)
    else:
        ax.set_yticklabels([])
        ax.tick_params(axis='y', which='both', left=True, labelleft=False, labelsize=16)
    
    #ax.legend(loc='lower right', fontsize=9)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim([0, 100])
    ax.set_ylim([0, 1])

# hide diagonal and lower triangle
for i in range(n_groups):
    for j in range(i+1): # diagonal and lower triangle
        axes[i, j].set_visible(False)

plt.tight_layout()

# --------------- (c) export results ---------------
if SAVE_FIGURE == 'yes':
    # Save piecewise regression figure
    pw_fig_name = f'piecewise_regression_{SITE}_nolabs.png'
    pw_fig_path = os.path.join(FIGPATH, pw_fig_name)
    plt.savefig(pw_fig_path, dpi=600, bbox_inches='tight')

plt.show()

# %% (11) THEMATIC GROUP LINE PLOTS

# --------------- (a) build all unique group pairs ---------------
# pairs = [(fg_list[i], fg_list[j], fg_label_list[i], fg_label_list[j])
#          for i in range(n_groups) for j in range(i+1, n_groups)]
pairs = [('hard_coral', 'soft_coral', 'Hard Coral', 'Soft Coral'),
         ('hard_coral', 'macroalgae', 'Hard Coral', 'Macroalgae'),
         ('hard_coral', 'sand', 'Hard Coral', 'Sand'),
         ('hard_coral', 'turf_cca', 'Hard Coral', 'Turf/Encrusting')]
n_pairs = len(pairs)

# --------------- (b) compute mean similarity per pair per pixel size ---------------
avg_similarity = (df.groupby(['group1', 'group2', 'pixel_size_m'])['jaccard_similarity']
                    .mean()
                    .reset_index())

# --------------- (c) create figure ---------------
fig, ax = plt.subplots(figsize=(10, 6))

cmap = plt.get_cmap('tab20', n_pairs)

for idx, (g1, g2, l1, l2) in enumerate(pairs):
    mask = (
        ((avg_similarity['group1'] == g1) & (avg_similarity['group2'] == g2)) |
        ((avg_similarity['group1'] == g2) & (avg_similarity['group2'] == g1))
    )
    pair_data = avg_similarity[mask].sort_values('pixel_size_m')

    if pair_data.empty:
        continue

    ax.plot(pair_data['pixel_size_m'], pair_data['jaccard_similarity'],
            label=f'{l1} / {l2}', color=cmap(idx), linewidth=2)

ax.set_xlabel('Pixel Size (m)', fontsize=22, fontweight='bold')
ax.set_ylabel('Likelihood of Co-occurrence', fontsize=22, fontweight='bold')
ax.set_ylim(MIN_JS, MAX_JS)
ax.set_xticks([0, 10, 20, 100, 300])
ax.set_xlim(0,300)
ax.tick_params(labelsize=16)

# legend outside the axes
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0,
          fontsize=9, title='Group pair', title_fontsize=10)

plt.tight_layout()

# --------------- (d) figure export ---------------
if SAVE_FIGURE == 'yes':
    name = f'{selected_gz}_similarity_lines.svg'
    full_path = os.path.join(FIGPATH, name)
    plt.savefig(full_path, dpi=600, bbox_inches='tight')

plt.show()