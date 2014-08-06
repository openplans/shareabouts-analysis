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
##url = 'http://api.shareabouts.org/api/v2/afraint/datasets/new_york_data/places'

url = 'http://api.shareabouts.org/api/v2/cb6/datasets/cb6capex/places'

url += '?format=json&include_private'

owner = url.split("/")[-4]
dataset_name = url.split("/")[-2]


data = api.pull_dataset_data(api.get_data(url), "features")




x_axis_hours = []
y_axis_place_adding = []
y_axis_commenting = []
y_axis_support = []
y_axis_other = []

activity = []


place_time = {'00':0, '01':0, '02':0, '03':0, '04':0, '05':0, '06':0,
              '07':0, '08':0, '09':0, '10':0, '11':0, '12':0, '13':0,
              '14':0, '15':0, '16':0, '17':0,'18':0, '19':0, '20':0,
              '21':0, '22':0, '23':0 }
comment_time = {'00':0, '01':0, '02':0, '03':0, '04':0, '05':0, '06':0,
              '07':0, '08':0, '09':0, '10':0, '11':0, '12':0, '13':0,
              '14':0, '15':0, '16':0, '17':0,'18':0, '19':0, '20':0,
              '21':0, '22':0, '23':0 }
support_time = {'00':0, '01':0, '02':0, '03':0, '04':0, '05':0, '06':0,
              '07':0, '08':0, '09':0, '10':0, '11':0, '12':0, '13':0,
              '14':0, '15':0, '16':0, '17':0,'18':0, '19':0, '20':0,
              '21':0, '22':0, '23':0 }
other_time = {'00':0, '01':0, '02':0, '03':0, '04':0, '05':0, '06':0,
              '07':0, '08':0, '09':0, '10':0, '11':0, '12':0, '13':0,
              '14':0, '15':0, '16':0, '17':0,'18':0, '19':0, '20':0,
              '21':0, '22':0, '23':0 }







for datum in data:
    created = datum["properties"]["created_datetime"]
    date_created = created.split("T")[0].split("-")
    time_created = created.split("T")[1].split(":")

    hour = str(time_created[0])
    minute = time_created[1]
    place_time[ hour ] += 1

    if len (datum["properties"]["submission_sets"]) > 0:
        for submission in datum["properties"]["submission_sets"]:
            print submission
            submission_url = datum["properties"]["submission_sets"][submission]['url']
            interactions = api.pull_dataset_data(api.get_data(submission_url), "results")
            for interaction in interactions:
                interact_created = interaction['created_datetime']
                time_created = interact_created.split("T")[1].split(":")
                hour = str(time_created[0])
                if submission == 'comments':
                    comment_time[ hour ] += 1
                elif submission == 'support':
                    support_time[ hour ] += 1
                else:
                    other_time[ hour ] += 1





file_name = owner + "_" + dataset_name + ".png"
output_file = os.path.join(os.getcwd(), "exports", "plots", file_name)






for hr in sorted(place_time):
    x_axis_hours.append(int(hr) )
    y_axis_place_adding.append( place_time[hr] )
    print hr, " -- ", place_time[hr]
    activity.append(place_time[hr])



for hr in sorted(comment_time):
    y_axis_commenting.append( comment_time[hr] )
    activity.append(comment_time[hr])

for hr in sorted(support_time):
    y_axis_support.append( support_time[hr] )
    activity.append(support_time[hr])

for hr in sorted(other_time):
    y_axis_other.append( other_time[hr] )
    activity.append(other_time[hr])








plt.plot(x_axis_hours, y_axis_place_adding,
         marker='s', linestyle='-', color='b', label='Adding Places')

plt.plot(x_axis_hours, y_axis_commenting,
         marker='o', linestyle='--', color='r', label='Commenting')

plt.plot(x_axis_hours, y_axis_support,
         marker='^', linestyle='--', color='g', label='Supporting')

plt.plot(x_axis_hours, y_axis_other,
         marker='v', linestyle='--', color='c', label='Other')


plt.xlabel('time')
plt.ylabel('number of interactions')
plt.title(owner + " // " + dataset_name)
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.grid(True)
ymax = max(activity) + 5
ymin = min(activity)

plt.axis([0, 24, ymin, ymax])
plt.xticks(x_axis_hours)
plt.legend(loc=2)

plt.savefig(output_file, transparent="True")

plt.show()






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