# Benthic Co-occurrence
Python code for calculation of co-occurrence metrics for benthic observational data derived from [ReefCloud](https://reefcloud.ai/) classified benthic photoquadrats. The Jaccard similarity metric is used as a proxy for co-occurrence likelihood between pairs of thematic classes for coral or seagrass environments, derived from benthic classes identified via automated image classification. The scripts here were used for the article **TBC**. The scripts presented here detail the process of:
1. Reclassification of classified benthic data into thematic classes relevant to remote sensing of coral/seagrass environments.
2. Calculation of presence/absence based co-occurrence metrics using the Jaccard similarity measure across various pixel sizes.
3. Statistical analysis of similarity results to identify pixel size thresholds and plotting of results.

# Benthic Reclassification
Each section of the script `01_reclassify_field_data.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [PyProj](https://pypi.org/project/pyproj/), [GeoPandas](https://pypi.org/project/geopandas/), [Shapely](https://pypi.org/project/shapely/), [glob](https://docs.python.org/3/library/glob.html), and [os](https://docs.python.org/3/library/os.html)

### (1) User Input
The key inputs for this script are defined here including: (a) the site ID used in the input data to identify the field site, (b) the working directory path, and (c) the remapping used to group the benthic classes from image classification into thematic classes used for subsequent co-occurrence calculations.

> [!NOTE]
> The remappings here are defined in two input files (`labelmap_reefcloud.csv` and `labelmap_coralnet.csv`) which are not provided. However, a similar remapping that is shown for the EB site in this script is used. Essentially, the detailed benthic data used as input is aggregated into simpler thematic classes, representing classes that are typically identified via satellite-based remote sensing approaches.

# Co-occurrence Calculation
Each section of the script `02_cooccurrence.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [SciPy](https://pypi.org/project/scipy/), [alive-progress](https://pypi.org/project/alive-progress/), and [os](https://docs.python.org/3/library/os.html)

# Benthic Reclassification
Each section of the script `03_summary_stats.py` is outlined here, including key processing steps and requirements from the user.

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [NumPy](https://pypi.org/project/numpy/), [SciPy](https://pypi.org/project/scipy/), [Matplotlib](https://pypi.org/project/matplotlib/), [seaborn](https://pypi.org/project/seaborn/), and [os](https://docs.python.org/3/library/os.html)
