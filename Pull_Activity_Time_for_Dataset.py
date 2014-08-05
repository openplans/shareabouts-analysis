# Activity Time for a dataset
"""

"""
import csv
import os


import settings
import helpers.api_access as api
import helpers.data_mgmt as mgmt

import matplotlib.pyplot as plt
import datetime

print "Loaded all modules and helper functions"

# make sure to "include_private"!
url = 'http://api.shareabouts.org/api/v2/afraint/datasets/new_york_data/places?format=json&include_private'

crash_data = api.pull_dataset_data(api.get_data(url), "features")

place_time = {}
comment_urls = []

for crash in crash_data:
    created = crash["properties"]["created_datetime"]
    date_created = created.split("T")[0].split("-")
    time_created = created.split("T")[1].split(":")

    hour = time_created[0]
    minute = time_created[1]

    if hour not in place_time:
        place_time[ hour ] = 1
    else:
        place_time[ hour ] += 1

    if len (crash["properties"]["submission_sets"]) > 0:
        for submission in crash["properties"]["submission_sets"]:
            submission_url = crash["properties"]["submission_sets"][submission]['url']
            comment_urls.append(submission_url)

            interactions = api.pull_dataset_data(api.get_data(submission_url), "results")
            for interaction in interactions:
                interact_created = interaction['created_datetime']
                time_created = interact_created.split("T")[1].split(":")
                hour = str(time_created[0])

                if hour not in comment_time:
                    comment_time[ hour ] = 1
                else:
                    comment_time[ hour ] += 1

for hr in sorted(place_time):
    print hr, " -- ", place_time[hr]


for hr in sorted(comment_time):
    print hr, " -- ", comment_time[hr]


#plt.plot([1,2,3,4], [1,4,9,16], 'ro')
#plt.axis([0, 6, 0, 20])
#plt.show()

output_file = os.path.join(os.getcwd(),
                           "exports",
                           "crashstories.csv")


'''


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
'''