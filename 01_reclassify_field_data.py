#read linked ReefCloud output and reformat into the desired co-occurrence classes
#Dylan Cowley: 28/01/2026

# input:
#   - {site}_{yearMonth}.csv

# output:
#   - reclassified field data into key benthic mapping categories

# %% (0) PACKAGE IMPORTS
import pandas as pd
import pyproj
import glob
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os

# %% (1) USER INPUT
# --------------- (a) define analysis parameters ---------------
SITE = 'HR' # define site: HR = Heron Reef, EB = Eastern Banks

# --------------- (b) define working directory ---------------
ROOT = r'C:\Users\dcowl\OneDrive - The University of Queensland\Work PC\Documents\02_smartsat\data\ReefCloud'

# --------------- (c) define remapping ---------------
# mapping to reassign: ReefCloud Benthic Class --> Thematic Group
if SITE == 'HR':
    input_fldr = ROOT+'/'+SITE+r'_data\FieldData\03_output_linked'
    output_fldr = ROOT+'/'+SITE+r'_data\FieldData\04_output_reclassified'
    filter_mapping_coralnet = pd.read_csv(os.path.join(output_fldr, 'labelmap_coralnet.csv'),
                                          low_memory=False)
    filter_mapping_reefcloud = pd.read_csv(os.path.join(output_fldr, 'labelmap_reefcloud.csv'),
                                          low_memory=False)
elif SITE == 'EB':
    input_fldr = ROOT+'/'+SITE+'_data'
    output_fldr = ROOT+'/'+SITE+'_data'
    filter_mapping = {
        'All.other': 'Other',
        'Anemone': 'Other',
        'Benthic.Microalgae.on.Sand': 'Sand',
        'Caulerpa': 'Algae',
        'CRED.Tape': 'Other',
        'CRED.Wand': 'Other',
        'Cyanobacteria': 'Other',
        'Cyanobacteria.smothering.dead.coral': 'Other',
        'Cymodocea.rotundata': 'Dense',
        'Cymodocea.serrulata': 'Dense',
        'Dead.seagrass': 'Other',
        'Echinoderms..Sea.stars': 'Other',
        'Echinoderms..sea.urchin': 'Other',
        'Halimeda': 'Algae',
        'Halodule.uninervis': 'Dense',
        'Halophila.ovalis': 'Sparse',
        'Halophila.spinulosa': 'Sparse',
        'hard.substrate.with.turf': 'Other',
        'Hydroclathrus': 'Algae',
        'Lyngbya.majuscula': 'Lyngbya',
        'Macroalgae.Other': 'Algae',
        'Macroalgae..Articulated.calcareous..green': 'Algae',
        'Microalgae': 'Algae',
        'muddy.sand': 'Sand',
        'Other': 'Other',
        'Other.hard.coral': 'Other',
        'Other.soft.coral': 'Other',
        'Out.of.focus': 'Other',
        'Padina': 'Algae',
        'Pinna': 'Other',
        'Sand': 'Sand',
        'Sargassum': 'Other',
        'Sea.cucumber': 'Other',
        'Seagrass': 'Other',
        'Shadow_TWS': 'Other',
        'Shell.hash.Gravel': 'Sand',
        'Sponge': 'Other',
        'Syringodium': 'Other',
        'Udotea.spp.': 'Algae',
        'Unknown': 'Other',
        'Zostera.muelleri': 'Dense'
    }

# %% (2) READ DATA
# --------------- (a) read data ---------------
# initialise list to store dataframes
df_list = []

# loop through all .csv files and combine them
for filename in glob.glob(input_fldr+'/'+'*.csv'):  
    # read the files
    df_raw = pd.read_csv(filename, low_memory=False)
    df_raw = df_raw.rename(columns=lambda x: x.strip()) # remove trailing spaces
    
    if SITE == 'HR': # extract year and month from filename
        year = int(filename[-10:-6])
        month = int(filename[-6:-4])
        year_month = filename[-10:-4]
    elif SITE == 'EB': # extract year and month from file
        year = [i.split('-')[0] for i in df_raw['year_month']] 
        month = [i.split('-')[1] for i in df_raw['year_month']] 
        year_month = [str(x) + str(y) for x, y in zip(year, month)]
    
    # remove extra, useless info
    if SITE == 'HR':
        if year < 2019: #CoralNet
            delcols = ['unique_id', 'survey_title', 'date (UTC)', 'year', 'site', 'depth_m',
                       'transect', 'total', 'project', 'survey_id', 'site_id']
            mapping = filter_mapping_coralnet
        else: # ReefCloud
            delcols = ['unique_id', 'survey_title', 'image_name', 'date (UTC)', 'site', 'depth_m',
                       'transect', 'total', 'project', 'survey_id', 'site_id', 'site_country_region',
                       'site_local_region', 'site_reef_name', 'month', 'yearmonth', 'PhotoName',
                       'year']
            mapping = filter_mapping_reefcloud
    elif SITE == 'EB':
        delcols = ['image_code', 'transect', 'bank', 'year_month', 'image_number',
                   'date', 'image_name', 'year', 'total', 'total_other',
                   'total_sessile invertebrate', 'total_microalgae',
                   'total_green macroalgae', 'total_seagrass', 'total_mobile invertebrate',
                   'total_brown macroalgae', 'total_lyngbya', 'total_macroalgae other']
    
    # only drop columns that exist in this dataframe
    df_temp = df_raw.drop(delcols, axis=1)
    
    # --------------- (b) aggregate classes ---------------
    fg = np.unique(mapping.functional_group) # unique thematic groups
    agg_classes = np.zeros((len(df_temp), len(fg))) # for storage
    
    for i in np.arange(0, len(fg)):
        TF = mapping.functional_group==fg[i] # select relevant columns
        cols_list = mapping.class_label[TF]
        cols_to_select = [x.strip() for x in cols_list] # strip away extra white space
        agg_classes[:,i] = df_temp[cols_to_select].sum(axis=1)
    
    # add year, month, and year_month columns
    df_year = pd.DataFrame(data = agg_classes, columns = fg)
    df_year.insert(0, 'year', year)
    df_year.insert(1, 'month', month)
    df_year.insert(2, 'year_month', year_month)
    
    # replace site_latitude and site_longitude columns with the correct data
    if year < 2019: # CoralNet
        df_year.insert(3, 'longitude', df_temp['site_longitude'])
        df_year.insert(4, 'latitude', df_temp['site_latitude'])
    else: # ReefCloud
        df_year.insert(3, 'longitude', df_temp['Longitude'])
        df_year.insert(4, 'latitude', df_temp['Latitude'])
    
    df_list.append(df_year)

# --------------- (c) combine dataframes ---------------
df_all = pd.concat(df_list, ignore_index=True, sort=False)
df = df_all.drop(columns='other') # remove "Other" column
fg_rem = [x for x in fg if x != 'other']
df['tot'] = df[fg_rem].sum(axis=1)

# --------------- (d) filter data ---------------
# remove rows where desired categories sum to < 90
df_filtered = df[df['tot'] >= 90]

# print summary of changes after filtering
print(f"All data rows: {len(df)}")
print(f"Rows with non-other sum >=90%: {len(df_filtered)}")
print(f"Removed rows: {((len(df)-len(df_filtered))/len(df))*100:.2f}%")

# %% (3) COORDINATE CONVERSION
# --------------- (a) convert lat/lon to UTM ---------------
lon = df_filtered['longitude'].iloc[0]
lat = df_filtered['latitude'].iloc[0]

# determine UTM zone automatically
utm_zone = int((lon+180)/6)+1
hemisphere = 'north' if lat >= 0 else 'south'

# create transformer from WGS84 to UTM
utm_crs = f"+proj=utm +zone={utm_zone} +{'north' if hemisphere == 'north' else 'south'} +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
transformer = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)

# --------------- (b) convert coordinates ---------------
utm_coords = transformer.transform(df_filtered['longitude'].values, 
                                 df_filtered['latitude'].values)

# --------------- (c) add UTM coordinates to dataframe ---------------
df_filtered.insert(5, 'X', utm_coords[0])
df_filtered.insert(6, 'Y', utm_coords[1])

# %% (4) DETERMINE GEOMORPHIC ZONE
# --------------- (a) read zone data ---------------
shp_fldr = input_fldr+'/GZ'
if SITE == 'HR':
    zone_shapefiles = {
        'Reef_Flat_Inner': 'Reef_Flat_Inner.shp',
        'Reef_Flat_Outer': 'Reef_Flat_Outer.shp', 
        'Reef_Slope_South': 'Reef_Slope_South.shp',
        'Reef_Slope_North': 'Reef_Slope_North.shp'
    }
elif SITE == 'EB':
    zone_shapefiles = {
        'Amity': 'bank_amity.shp',
        'Chain': 'bank_chain.shp', 
        'Maroom': 'bank_maroom.shp',
        'Moreton': 'bank_moreton.shp',
        'WangaWallen': 'bank_wanga.shp'
    }
df_filtered.insert(6, 'geomorphic_zone', 'Unkown') # placeholder

if hemisphere == 'north':
    points_crs = f"EPSG:{32600 + utm_zone}" # UTM North
else:
    points_crs = f"EPSG:{32700 + utm_zone}" # UTM South

# --------------- (b) extract points from shapefiles ---------------
geometry = [Point(x, y) for x, y in zip(df_filtered['X'], df_filtered['Y'])]
points_gdf = gpd.GeoDataFrame(df_filtered, geometry=geometry, crs=points_crs)

zone_assignments = {} # track which points get assigned to which zones
points_assigned = set() # track which points have been assigned

for zone_name, shapefile_name in zone_shapefiles.items():
    shapefile_path = os.path.join(shp_fldr, shapefile_name)
    
    # read the zone shapefile
    zone_gdf = gpd.read_file(shapefile_path)

    # reproject zone shapefile to match points if necessary
    if zone_gdf.crs != points_gdf.crs:
        zone_gdf = zone_gdf.to_crs(points_gdf.crs)
    
    # perform spatial join for this zone
    joined = gpd.sjoin(points_gdf, zone_gdf, how='inner', predicate='within')
    
    if len(joined) > 0:
        # get indices of points that fall within this zone
        point_indices = joined.index.unique()
        
        # assign zone name to these points
        for idx in point_indices:
            if idx not in points_assigned: # only assign if not already assigned
                df_filtered.loc[idx, 'geomorphic_zone'] = zone_name
                points_assigned.add(idx)
                
                if zone_name not in zone_assignments:
                    zone_assignments[zone_name] = []
                zone_assignments[zone_name].append(idx)
        

total_assigned = len(points_assigned)
total_unknown = len(df_filtered)-total_assigned

# for error checking
print(f"\nTotal points assigned: {total_assigned}")
print(f"Total points unassigned (Unknown): {total_unknown}")

# %% (5) SAVE OUTPUT
df_filtered.to_csv(os.path.join(output_fldr, SITE+'_benthic.csv'))