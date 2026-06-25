# Benthic Co-occurrence
Python code for calculation of co-occurrence metrics for benthic observational data derived from [ReefCloud](https://reefcloud.ai/) classified benthic photoquadrats (see [Roelfsema et al. (2021)](https://doi.org/10.3389/fmars.2021.643381) and [Golding et al. (2026)](https://doi.org/10.48610/7df1430) for details). The Jaccard similarity metric is used as a proxy for co-occurrence likelihood between pairs of thematic classes for coral or seagrass environments, derived from benthic classes identified via automated image classification. The scripts here were used for the article **TBC**. The scripts presented here detail the process of:
1. Reclassification of classified benthic data into thematic classes relevant to remote sensing of coral/seagrass environments.
2. Calculation of presence/absence based co-occurrence metrics using the Jaccard similarity measure across various pixel sizes.
3. Statistical analysis of similarity results to identify pixel size thresholds and plotting of results.

# Benthic Reclassification
Each section of the script `01_reclassify_field_data.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [PyProj](https://pypi.org/project/pyproj/), [GeoPandas](https://pypi.org/project/geopandas/), [Shapely](https://pypi.org/project/shapely/), [glob](https://docs.python.org/3/library/glob.html), and [os](https://docs.python.org/3/library/os.html)

The key inputs for this script are defined in the USER INPUT section, including: (a) the site ID used in the input data to identify the field site, (b) the working directory path, and (c) the remapping used to group the benthic classes from image classification into thematic classes used for subsequent co-occurrence calculations.

> [!NOTE]
> The remappings here are defined in two input files (`labelmap_reefcloud.csv` and `labelmap_coralnet.csv`) which are not provided. However, a similar remapping that is shown for the EB site in this script is used. Essentially, the detailed benthic data used as input is aggregated into simpler thematic classes, representing classes that are typically identified via satellite-based remote sensing approaches.

Data is read from the input `.csv` files, then aggregated into broader thematic classes. Extra data is removed and column headers are checked for consistency, to streamline further processing. A filter is applied to the dataset to remove photoquadrats where <90% of the defined benthic cover is **not** covered by the desired thematic classes. For example, if an input point is comprised of >10% "Other" (mobile invertebrates, fish, survey gear, etc.) it is removed from the dataset. Further quality controls are focused on confirming coordinates and assigning each point to a geomorphic zone or subregion within the study site.

# Co-occurrence Calculation
Each section of the script `02_cooccurrence.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [SciPy](https://pypi.org/project/scipy/), [alive-progress](https://pypi.org/project/alive-progress/), and [os](https://docs.python.org/3/library/os.html)

Key user inputs for this script include:
- Site ID and benthic type (e.g., coral or seagrass) to help read the correct datasets and to define further parameters specific to each site.
- Pixel sizes used for presence/absence assignment and similarity calculations.
- The specified geomorphic zone/subregion in which to perform the calculations.
- Temporal range to use from the full dataset.
- Input/output directory paths to load and save data.

The remainder of the script will then apply spatial filters to perform calculations in the desired zone, before conducting the similarity analysis on the filtered subset. Presence/absence matrices are constructed for each unique thematic class pair, based on the aggregated classes from the previous script. The pixel sizes are used to define the search radius around each point to identify which benthic features are present within difference pixels across the study site. The presence/absence matrices are then used to determine the Jaccard similarity metric, used here as a proxy for co-occurrence likelihood. Basic statistics (e.g., mean and variance) are calculated from the similarity metrics calculated across each year, geomorphic zone, and pixel size.

The Jaccard calculation is as follows:
$J(B_i, B_j) = \dfrac{|B_i \cap B_j|}{|B_i \cup B_j|} = \dfrac{|B_i \cap B_j}{|B_i|+|B_j|-|B_i \cap B_j|}
For $i=1,...,n$ and $j=1,...,m$ where $J(B_i, B_j)$ is the Jaccard similarity index, $\cap$ represents the intersection and $\cup$ represents the union between two sets of benthic features. $B_i$ represents the presence of features from the first benthic group, and $B_j$ represents presence from the second group.

# Summary Statistics
Each section of the script `03_summary_stats.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [SciPy](https://pypi.org/project/scipy/), [Matplotlib](https://pypi.org/project/matplotlib/), [seaborn](https://pypi.org/project/seaborn/), and [os](https://docs.python.org/3/library/os.html)

Similar user inputs are required here as with the other scripts, with the addition of plotting parameters and a switching variable to control figure export. Data is read and filtered for the desired temporal range and geomorphic zone/subregion before the computed Jaccard similarity scores are plotted using heatmaps, to identify co-occurrence likelihoods between different thematic class pairs. Further plots are created to track the trends of similarity as pixel size increases using a logistic regression, followed by segmented regression to identify critical pixel size thresholds in benthic co-occurrence between each thematic pair.

# References
- Roelfsema, C.M., Lyons, M., Murray, N., Kovacs, E.M., Kennedy, E., Markey, K., Borrego-Acevedo, R., Ordonez-Alvarez, A., Say, C., Tudman, P., Roe, M., Wolff, J., Traganos, D., Asner, G.P., Bambic, B., Free, B., Fox, H.E., Lieb, Z., Phinn, S.R., 2021. Workflow for the Generation of Expert-Derived Training and Validation Data: A View to Global Scale Habitat Mapping. Frontiers in Marine Science, 8, 643381. [https://doi.org/10.3389/fmars.2021.643381](https://doi.org/10.3389/fmars.2021.643381)
- Golding, K.M., Smart, J.N., Cowley, D., Carrasco Rivera, D.E., Hammerman, N.M., Markey, K., Kovacs, E., Diederiks, F.F., Passenger, J., Roelfsema, C.M., 2026. Georeferenced benthic photo quadrats and benthic cover data derived from a time series of transect surveys for Heron Reef flat and slope areas, Great Barrier Reef, 2019-2025. The University of Queensland, Data Collection. [https://doi.org/10.48610/7df1430](https://doi.org/10.48610/7df1430)
