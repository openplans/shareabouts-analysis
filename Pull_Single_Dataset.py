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




URLS = ['http://api.shareabouts.org/api/v2/afraint/datasets/new_york_data/places']


for url in URLS:
    print url
    # make sure to "include_private"!
    url += '?format=json&include_private'

    owner = url.split("/")[-4]
    dataset_name = url.split("/")[-2]

    filename = 'exports/excel/' + owner + "_" + dataset_name + ".xlsx"
    print filename

    data = api.pull_dataset_data(api.get_data(url), "features")


    ###################################################################
    # activity by day
    ###################################################################


    activity = {}



    for datum in data:
        date = str( datum['properties']['created_datetime'].split("T")[0] )

        if date in activity:
            activity[date] += 1
        else:
            activity[date] = 1


    ###################################################################
    # activity by time of day
    ###################################################################

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

###################################################################
###################################################################
# WRITE THE DATA TO EXCEL AND VISUALIZE
###################################################################
###################################################################

workbook = xlsxwriter.Workbook(filename)

worksheet_summary = workbook.add_worksheet( "SUMMARY" )

worksheet = workbook.add_worksheet( "github-calendar" )

worksheet1 = workbook.add_worksheet( "activity_hr" )
##worksheet2 = workbook.add_worksheet( "comment_time" )
##worksheet3 = workbook.add_worksheet( "support_time" )



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






activity = []
for hour in sorted(place_time):
    activity.append( [ hour, place_time[hour] ] )

print activity
# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.

###for dataset, worksheet in [[place_time, worksheet1]]:
row = 0
worksheet1.write_row(row, col, ['hr', 'places', 'comments', 'supports'])
row += 1
col = 0
for hour in sorted(place_time):
    worksheet1.write(row, col,     hour )
    worksheet1.write(row, col + 1, place_time[hour])
    worksheet1.write(row, col + 2, comment_time[hour])
    worksheet1.write(row, col + 3, support_time[hour])
    row += 1


# chart time
chart = workbook.add_chart({'type': 'line'})


chart.set_title({
    'name': 'Map Activity by Hour of Day',
    'name_font': {
        'name': 'Calibri',
    },
})


chart.add_series({
                    'values':     '=activity_hr!B2:B25',
                    'categories': '=activity_hr!A2:A25',
                    'line':           {'color': 'red'},
                    'name':             'places added',
                })

chart.add_series({
                    'values':     '=activity_hr!C2:C25',
                    'categories': '=activity_hr!A2:A25',
                    'line':           {'color': 'green'},
                    'name':             'comments',
                })

chart.add_series({
                    'values':     '=activity_hr!D2:D25',
                    'categories': '=activity_hr!A2:A25',
                    'line':           {'color': 'blue'},
                    'name':             'supports',
                })

chart.set_y_axis({
    'major_gridlines': {
        'visible': True,
        'line': {'width': 0.75, 'dash_type': 'dash'}
    },
})


chart.set_x_axis({
    'major_gridlines': {
        'visible': True,
        'line': {'width': 0.75, 'dash_type': 'dash'}
    },
})


worksheet_summary.insert_chart('B2', chart)

workbook.close()