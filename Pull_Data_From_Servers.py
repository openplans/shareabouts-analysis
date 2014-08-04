# Dataset Lifetime
"""
    Goes through every place in every dataset to get a start/end date for the
    overall dataset's lifetime.

    It takes a long time to run, but works.
"""
import csv
import os
import time
from time import sleep
import requests
from requests.auth import HTTPBasicAuth

import settings
import helpers.api_access as api
import helpers.data_mgmt as mgmt


print "Loaded all modules and helper functions"


data_url = 'http://data.shareabouts.org/api/v2/~/datasets?format=json&page=1'
api_url = 'http://api.shareabouts.org/api/v2/~/datasets?format=json&page=1'

data_server = api.get_data(data_url)
api_server = api.get_data(api_url)

DATA_datasets = api.pull_dataset_data(data_server, "results")
API_datasets = api.pull_dataset_data(api_server, "results")

# quick QAQC - make sure the json metadata matches the resulting python object
if len(DATA_datasets) != data_server["metadata"]["length"]:
    print "Error with DATA server data"
else:
    print "DATA server: %i datasets" % len(DATA_datasets)

if len(API_datasets) != api_server["metadata"]["length"]:
    print "Error with API server data"
else:
    print "API server: %i datasets" % len(API_datasets)


# combine the datasets from the API and DATA servers
API_data = api.pull_relevant_data(API_datasets)
DATA_data = api.pull_relevant_data(DATA_datasets)

all_data = {}

mgmt.combine_datasets(DATA_data, all_data)
mgmt.combine_datasets(API_data, all_data)
print len(all_data)

output_file = os.path.join(os.getcwd(),
                           "data_exports",
                           "all_datasets.csv")


mgmt.write_csv(output_file,
          ["owner", "owner_url",
          "display_name", "slug",
          "places", "place_URL",
          "comments", "supports", "other_interactions", "other_interaction_types",
          "first_place", "last_place"],
          all_data)
