# Benthic Co-occurrence
Python code for calculation of co-occurrence metrics for benthic observational data derived from [ReefCloud](https://reefcloud.ai/) classified benthic photoquadrats. The Jaccard similarity metric is used as a proxy for co-occurrence likelihood between pairs of thematic classes for coral or seagrass environments, derived from benthic classes identified via automated image classification. The scripts here were used for the article **TBC**. The scripts presented here detail the process of:
1. Reclassification of classified benthic data into thematic classes relevant to remote sensing of coral/seagrass environments.
2. Calculation of presence/absence based co-occurrence metrics using the Jaccard similarity measure across various pixel sizes.
3. Statistical analysis of similarity results to identify pixel size thresholds and plotting of results.

# Benthic Reclassification
_See_ `01_reclassify_field_data.py`

> [!IMPORTANT]
> **Required modules** to run this script:
> [Pandas](https://pypi.org/project/pandas/), [PyProj](https://pypi.org/project/pyproj/), [Glob](https://docs.python.org/3/library/glob.html), [GeoPandas](https://pypi.org/project/geopandas/), [NumPy](https://pypi.org/project/numpy/), [Shapely](https://pypi.org/project/shapely/), and [os](https://docs.python.org/3/library/os.html)

# Co-occurrence Calculation
_See_ `02_cooccurrence.py`

## Required Packages
This processing script requires the following modules to function:
- [Pandas](https://pypi.org/project/pandas/)
- [NumPy](https://pypi.org/project/numpy/)
- [SciPy](https://pypi.org/project/scipy/)
- [alive-progress](https://pypi.org/project/alive-progress/)
- [os](https://docs.python.org/3/library/os.html)

# Benthic Reclassification
_See_ `03_summary_stats.py`

## Required Packages
This processing script requires the following modules to function:
- [Pandas](https://pypi.org/project/pandas/)
- [NumPy](https://pypi.org/project/numpy/)
- [SciPy](https://pypi.org/project/scipy/)
- [Matplotlib](https://pypi.org/project/matplotlib/)
- [seaborn](https://pypi.org/project/seaborn/)
- [os](https://docs.python.org/3/library/os.html)
