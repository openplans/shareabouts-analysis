# Activity Time for a dataset
"""

"""
import csv
import os


import settings
import helpers.api_access as api
import helpers.data_mgmt as mgmt


import datetime

import xlsxwriter



print "Loaded all modules and helper functions"




URLS = ['http://data.shareabouts.org/api/v2/chicagobikes/datasets/chicago-bike-parking/places']


for url in URLS:
    print url
    # make sure to "include_private"!
    url += '?format=json&include_private'

    owner = url.split("/")[-4]
    dataset_name = url.split("/")[-2]


    data = api.pull_dataset_data(api.get_data(url), "features")




    activity = {}



    for datum in data:
        date = str( datum['properties']['created_datetime'].split("T")[0] )

        if date in activity:
            activity[date] += 1
        else:
            activity[date] = 1

######################################
########################################

workbook = xlsxwriter.Workbook('exports/excel/calendar.xlsx')
worksheet = workbook.add_worksheet( "github-calendar" )

first_date = datetime.datetime.strptime( sorted(activity)[0], '%Y-%m-%d')

data_to_write = []


labels = workbook.add_format({'bold':True})
data_format = workbook.add_format( {'align':'center',
                                    'valign':'vcenter',
                                } )
#data_format.set_border()

for date in sorted(activity):
    the_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    day_of_week = the_date.strftime('%a')

    days_out = the_date - first_date

    if days_out > datetime.timedelta(1):
        weeks_out = int( str(days_out).split(" ")[0]) / 7
    else:
        weeks_out = 0

    print date, day_of_week, activity[date], days_out, weeks_out

    if day_of_week == 'Sun': row = 0
    elif day_of_week == 'Mon': row = 1
    elif day_of_week == 'Tue': row = 2
    elif day_of_week == 'Wed': row = 3
    elif day_of_week == 'Thu': row = 4
    elif day_of_week == 'Fri': row = 5
    elif day_of_week == 'Sat': row = 6

    col = weeks_out + 1

    #data_to_write.append( [row, col, activity[date]] )

    worksheet.write(row, col, activity[date], data_format )


days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'weeks out:']
worksheet.write_column(0,0,days, labels)

weeks = range(weeks_out+1)
worksheet.write_row(7,1,weeks, labels)

worksheet.write(8, 0, "first date: " + str(first_date))


for num in range(7):
    worksheet.set_row(num, 30)

worksheet.freeze_panes(0, 1)

worksheet.conditional_format('B1:ZZ7', {'type': '3_color_scale',
                                         'min_color': "#C5D9F1",
                                         'mid_color': "#8DB4E3",
                                         'max_color': "#538ED5"})


##worksheet.set_column(1, weeks_out+ 1, 5)

workbook.close()


'''

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

    '''
