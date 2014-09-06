# Dataset Lifetime
"""
    Goes through every place in every dataset to get a start/end date for the
    overall dataset's lifetime.

    It takes a long time to run, but works.
"""
import csv
import os
import time
import datetime
from time import sleep
import requests
from requests.auth import HTTPBasicAuth

import settings
import helpers.api_access as api
import helpers.data_mgmt as mgmt


OUTPUT_FILENAME = "Both_Servers_w_lifetime_" + \
                    str(datetime.date.today()) + \
                    ".csv"


def history_of_dataset(PLACES_URL):
    """ identifies the first and last date that places
        were added to the dataset """
    JSON = api.get_data(PLACES_URL)
    print PLACES_URL
    # change the cutoff number to prevent large datasets from being processed
    if JSON["metadata"]["length"] > 1000:
        return "Too Many", "Too Many"
    else:
        all_places = api.pull_dataset_data(JSON, "features")
        all_dates = []
        for place in all_places:
            created = str(place["properties"]["created_datetime"].split("T")[0])
            if created not in all_dates:
                all_dates.append(created)
        if len(all_dates) > 0:
            first_place = sorted(all_dates)[0]
            last_place = sorted(all_dates)[-1:][0]
            return first_place, last_place
        else:
            return "No places", "No places"

def pull_relevant_data(JSON):
    print "PULLING RELEVANT DATA"
    """  this is where the data of interest is pulled out of a JSON dictionary
         and tossed into a list  """
    results = []
    for dataset in JSON:
        # get the number and type of non-point user interaction
        interactions = {"comments":0, "support":0, "other":0}
        types_of_interaction = []
        for item in dataset["submission_sets"]:
            if item == "comments":
                interactions["comments"] += dataset["submission_sets"][item]["length"]
            elif item == "support":
                interactions["support"] += dataset["submission_sets"][item]["length"]
            else:
                interactions["other"] += dataset["submission_sets"][item]["length"]
                types_of_interaction.append(str(item))

        # isolate the username and dump the data into a list
        owner_name = str(dataset["owner"].split("/")[-1:][0] )

        ##first_point, last_point = None, None
        first_point, last_point = history_of_dataset(dataset["places"]["url"])
        print first_point, last_point

        data = [ owner_name.encode('utf8'),               # 0
                 dataset["owner"].encode('utf8'),         # 1
                 dataset["display_name"].encode('utf8'),  # 2
                 dataset["slug"].encode('utf8'),          # 3
                 dataset["places"]["length"],             # 4
                 dataset["places"]["url"],                # 5
                 interactions["comments"],                # 6
                 interactions["support"],               # 7
                 interactions["other"],             # 8
                 types_of_interaction,          # 9
                 first_point, last_point  ]               # 10, 11
        results.append( data )
    return results






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
####API_data = api.pull_relevant_data(API_datasets)
API_data = pull_relevant_data(API_datasets)
DATA_data = pull_relevant_data(DATA_datasets)

all_data = {}

mgmt.combine_datasets(DATA_data, all_data)
mgmt.combine_datasets(API_data, all_data)
print len(all_data)

output_file = os.path.join(os.getcwd(),
                           "exports", "data",
                           OUTPUT_FILENAME)


mgmt.write_csv(output_file,
          ["owner", "owner_url",
          "display_name", "slug",
          "places", "place_URL",
          "comments", "supports", "other_interactions", "other_interaction_types",
          "first_place", "last_place"],
          all_data)
