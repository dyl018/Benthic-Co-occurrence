# Benthic Co-occurrence
Python code for calculation of co-occurrence metrics for benthic observational data derived from [ReefCloud](https://reefcloud.ai/) classified benthic photoquadrats. The Jaccard similarity metric is used as a proxy for co-occurrence likelihood between pairs of thematic classes for coral or seagrass environments, derived from benthic classes identified via automated image classification. The scripts presented here detail the process of:
1. Reclassification of classified benthic data into thematic classes relevant to remote sensing of coral/seagrass environments.
2. Calculation of presence/absence based co-occurrence metrics using the Jaccard similarity measure across various pixel sizes.
3. Statistical analysis of similarity results to identify pixel size thresholds and plotting of results.

# Benthic Reclassification
_See_ `01_reclassify_field_data.py`
