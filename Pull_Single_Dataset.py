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

URLS = ['http://data.shareabouts.org/api/v2/nycdot/datasets/vz/places']
###URLS = ['http://api.shareabouts.org/api/v2/openplans/datasets/atm_surcharge/places']
###URLS = ['http://api.shareabouts.org/api/v2/afraint/datasets/new_york_data/places']
##URLS = ['http://api.shareabouts.org/api/v2/jjones/datasets/cogo/places']
##URLS = ['http://data.shareabouts.org/api/v2/divvy/datasets/divvy/places']
##URLS = ['http://data.shareabouts.org/api/v2/ourmiami/datasets/psc2014/places']
##URLS = ['http://api.shareabouts.org/api/v2/afraint/datasets/new_york_data/places']
##URLS = ['http://api.shareabouts.org/api/v2/dksassociates/datasets/lane/places']


for url in URLS:
    print url
    # make sure to include private and submissions
    url += '?format=json&include_private&include_submissions'

    owner = url.split("/")[-4]
    dataset_name = url.split("/")[-2]

    filename = 'exports/excel/' + owner + "_" + dataset_name + ".xlsx"
    print filename

    data = api.pull_dataset_data(api.get_data(url), "features")


    ###################################################################
    # activity by day
    ###################################################################

    activity = {}

    all_submissions = []
    # [ [unique ID, date, submissiontype], ...     ]

    unique_submissions = {}
    # { submissiontype1:{date:[ [un1,un2,...],total,unique], ... }, ...    }


    place_adders = {}
    unique_adders = {}

    activity_by_day_of_week = {'Sun':0, 'Mon':0, 'Tue':0, 'Wed':0,'Thu':0,'Fri':0,'Sat':0}
    interaction_by_day_of_week = {'comments': {'Sun':0, 'Mon':0, 'Tue':0, 'Wed':0,'Thu':0,'Fri':0,'Sat':0},
                                    'support': {'Sun':0, 'Mon':0, 'Tue':0, 'Wed':0,'Thu':0,'Fri':0,'Sat':0},
                                    'other': {'Sun':0, 'Mon':0, 'Tue':0, 'Wed':0,'Thu':0,'Fri':0,'Sat':0},
                                  }


    for datum in data:
        # identify the day the place was added
        date = str( datum['properties']['created_datetime'].split("T")[0] )

        day_of_week = mgmt.get_day_of_week(date)
        activity_by_day_of_week[ day_of_week ] += 1

        # get the user id for the place adder
        try:
            adderID = datum["properties"]["user_token"]
        except:
            try:
               adderID = datum["properties"]['submitter_name']
            except:
                try:
                    adderID = datum["properties"]['submitter']["name"]
                except:
                    try:
                        adderID = datum["properties"]['private-email']
                    except:
                         adderID = 'ANON'
        if adderID == '': adderID = 'ANON'
        #print adderID

        if date not in place_adders:
            place_adders[date] = []
        if adderID not in place_adders[date]:
            place_adders[date].append(adderID)


        # for all submission sets related to this map point:
        #     figure out who the user was
        if datum['properties']['submission_sets']:
            for submission_typ in datum['properties']['submission_sets']:
                for action in datum['properties']['submission_sets'][submission_typ]:
                    submission_date = str( action['created_datetime'].split("T")[0] )
                    sub_day_of_week = mgmt.get_day_of_week(submission_date)
                    try:
                        interaction_by_day_of_week[submission_typ][sub_day_of_week]+=1
                    except:
                        interaction_by_day_of_week['other'][sub_day_of_week]+=1
                    try:
                        subID = action["user_token"]
                    except:
                        try:
                            try:
                                subID = action['submitter']['id']
                            except:
                                try:
                                    subID = action['submitter_name']
                                except:
                                    subID = 'ANON'
                                    print action
                        except:
                            print 'no usable ID value'
                    if subID == '': subID = 'ANON'
                    all_submissions.append( [subID, submission_date, submission_typ] )


        if date in activity: activity[date] += 1
        else:                activity[date] = 1

    # count up the unique people adding places for each day
    for date in place_adders:
        unique_adders[date] = len(place_adders[date])

    # count the number of brand-new people adding places each day
    already_added = []
    returning_visitors = {}
    new_visitors = {}
    for date in sorted(place_adders):
        for adder in place_adders[ date ]:
            if adder not in already_added:
                if date not in new_visitors:
                    new_visitors[date] = 1
                else:
                    new_visitors[date] += 1
                already_added.append(adder)
            else:
                if date not in returning_visitors:
                    returning_visitors[date] = 1
                else:
                    returning_visitors[date] += 1

    # count the number of brand-new people supporting/commenting/other each day
    already_added_commenters = []
    returning_commenters = {}
    new_commenters = {}

    # organize the submissions into unique and total user interaction
    # values for each date
    for sub in all_submissions:
        the_user = sub[0]
        the_date = sub[1]
        the_type = sub[2]






        if the_type not in unique_submissions:
            unique_submissions[the_type] = {}
        else:
            if the_date not in unique_submissions[the_type]:
                unique_submissions[the_type][the_date] = [[],0,0]
            # increment the total only if the user already interacted that day
            if the_user in unique_submissions[the_type][the_date][0]:
                unique_submissions[the_type][the_date][1] += 1
            else:
                # otherwise, increment the total and unique number. record the userid
                unique_submissions[the_type][the_date][1] += 1
                unique_submissions[the_type][the_date][2] += 1
                unique_submissions[the_type][the_date][0].append(the_user)


#    for typ in unique_submissions:
#        for date in sorted (unique_submissions[typ]):
#            print date, unique_submissions[typ][date][1], unique_submissions[typ][date][2]
#            print '\t', unique_submissions[typ][date][0]

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
            for submission_typ in datum["properties"]["submission_sets"]:
                ##print submission_typ
                ##print datum["properties"]["submission_sets"]
                for interaction in datum["properties"]["submission_sets"][submission_typ]:
                ##submission_url = datum["properties"]["submission_sets"][submission]['url']
                ##interactions = api.pull_dataset_data(api.get_data(submission_url), "results")
                ##for interaction in interactions:
                    interact_created = interaction['created_datetime']
                    time_created = interact_created.split("T")[1].split(":")
                    hour = str(time_created[0])
                    if submission_typ == 'comments':
                        comment_time[ hour ] += 1
                    elif submission_typ == 'support':
                        support_time[ hour ] += 1
                    else:
                        other_time[ hour ] += 1

###################################################################
###################################################################
# PREPARE TO WRITE THE DATA TO EXCEL AND VISUALIZE
###################################################################
###################################################################

workbook = xlsxwriter.Workbook(filename)

worksheet = workbook.add_worksheet( "Calendar-Heatmap" )
worksheet_summary = workbook.add_worksheet( "SUMMARY" )

worksheet1 = workbook.add_worksheet( "activity_hr" )

worksheet2 = workbook.add_worksheet( "activity_dayofweek" )


title_format = workbook.add_format({'bold':True,
                                    'font_size': 16})
labels = workbook.add_format({'bold':True,
                              'align':'center'})
data_format = workbook.add_format( {'align':'center',
                                    'valign':'vcenter',
                                      'border':5,
                                      'border_color':'white',
                                } )
border_format = workbook.add_format( {'border':5,
                                      'border_color':'white',
                                } )

null_format = workbook.add_format( {
                                    'bg_color': '#F0F0F0'
                                })

blue_cond_format = {'type': '3_color_scale',
                                             'min_color': "#C5D9F1",
                                             'mid_color': "#8DB4E3",
                                             'max_color': "#538ED5"}


red_cond_format = {'type': '3_color_scale',
                                             'max_color': "#b55353",
                                             'mid_color': "#c78554",
                                             'min_color': "#d9c454"}

green_cond_format = {'type': '3_color_scale',
                                             'max_color': "#008844",
                                             'mid_color': "#00BB5E",
                                             'min_color': "#C7F3CF"}

purp_cond_format = {'type': '3_color_scale',
                                             'max_color': "#AA0BAA",
                                             'mid_color': "#F14CF1",
                                             'min_color': "#F7BFF7"}



###################################################################
###################################################################
# WRITE THE CALENDAR HEATMAPS
###################################################################
###################################################################
data_to_write = []

first_date = datetime.datetime.strptime( sorted(activity)[0], '%Y-%m-%d')

def write_github_calendar(THE_TITLE, ACTIVITY, WORKSHEET, START_ROW, START_DATE,
                                    LABEL_FORMAT, DATA_FORMAT,
                                    BORDER_FORMAT, NULL_FORMAT, TITLE_FORMAT, COND_FORMATTING):
    """   makes a github-contribution-styled activity calendar heatmap in excel """

    for date in sorted(ACTIVITY):
        the_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        day_of_week = the_date.strftime('%a')

        days_out = the_date - START_DATE

        if days_out > datetime.timedelta(1):
            weeks_out = int( str(days_out).split(" ")[0]) / 7
        else:
            weeks_out = 0

        if day_of_week == 'Sun':   row = START_ROW
        elif day_of_week == 'Mon': row = START_ROW + 1
        elif day_of_week == 'Tue': row = START_ROW + 2
        elif day_of_week == 'Wed': row = START_ROW + 3
        elif day_of_week == 'Thu': row = START_ROW + 4
        elif day_of_week == 'Fri': row = START_ROW + 5
        elif day_of_week == 'Sat': row = START_ROW + 6

        col = weeks_out + 1

        # write the data for the individual date
        WORKSHEET.write(row, col, ACTIVITY[date], DATA_FORMAT )

    # write out the labels
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'weeks out:']
    WORKSHEET.write_column(START_ROW,0,days, LABEL_FORMAT)
    weeks = range(weeks_out+1)
    WORKSHEET.write_row(START_ROW + 7, 1, weeks, LABEL_FORMAT)
    WORKSHEET.write(START_ROW - 1, 0, THE_TITLE, TITLE_FORMAT)

    # conditional formatting here
    row_range = "B" + str(START_ROW + 1) + ":ZZ" + str(START_ROW+7)
    WORKSHEET.conditional_format(row_range, COND_FORMATTING)
    WORKSHEET.conditional_format(row_range, {'type': 'cell',
                                             'criteria': "=",
                                             'value': 0,
                                             'format': NULL_FORMAT})
    # page formatting - freeze pane and set cell widths/heights
    WORKSHEET.freeze_panes(0, 1)
    WORKSHEET.set_column(0,0, 40)
    for num in range(START_ROW, START_ROW + 7):
        WORKSHEET.set_row(num, 30, BORDER_FORMAT)



starting_row = 1

worksheet.write(0, 0, str(first_date).split(" ")[0], title_format)

starting_row += 1

title = "Total Places Added Per Day"
write_github_calendar(title,
                        activity, worksheet, starting_row, first_date, labels,
                        data_format, border_format, null_format, title_format, green_cond_format)


# now do the number of unique people adding places
starting_row += 10
title = "Total People Adding Places"
write_github_calendar(title, unique_adders, worksheet, starting_row, first_date, labels,
                                data_format, border_format, null_format, title_format, red_cond_format)


#
starting_row += 10
title = "New Visitors Adding Places"
write_github_calendar(title, new_visitors, worksheet, starting_row, first_date, labels,
                                data_format, border_format, null_format, title_format, red_cond_format)


#
starting_row += 10
title = "Returning Visitors Adding Places"
write_github_calendar(title, returning_visitors, worksheet, starting_row, first_date, labels,
                                data_format, border_format, null_format, title_format, red_cond_format)


# this is the ratio of places to unique adders
starting_row += 10
place_ratio = {}
for date in activity:
    ratio = float(unique_adders[date]) / float(activity[date])
    if ratio == 1 and activity[date] == 1: pass
    else:
        place_ratio[date] = ratio
title = "Ratio of (Unique People/Total Places).             Darker = more diversity in the activity. lighter = more single-person activity "
write_github_calendar(title,
                        place_ratio, worksheet, starting_row, first_date, labels,
                        data_format, border_format, null_format, title_format, purp_cond_format)



# this is total interactions
starting_row += 10
types = ""
all_interactions = {}
for typ in unique_submissions:
    types += (typ + " & ")
    for date in unique_submissions[typ]:
        if date not in all_interactions:
            all_interactions[date] = unique_submissions[typ][date][1]
        else:
            all_interactions[date] += unique_submissions[typ][date][1]
title = "Total Interactions per day- " + types[:-3]
write_github_calendar(title,
                        all_interactions, worksheet, starting_row, first_date, labels,
                        data_format, border_format, null_format, title_format, green_cond_format)



# now do the number of unique people interacting
starting_row += 10
total_people = {}

for typ in unique_submissions:

    for date in unique_submissions[typ]:
        if date not in total_people:
            total_people[date] = []

        for person in unique_submissions[typ][date][0]:
            if person not in total_people[date]:
                total_people[date].append(person)
date_dict = {}
for date in total_people:
    date_dict[date] = len(total_people[date])
title = "Total People Adding " + types[:-3]
write_github_calendar(title, date_dict, worksheet, starting_row, first_date, labels,
                         data_format, border_format, null_format, title_format, red_cond_format)




##############
#############
## HOW MANY PEOPLE ARE FIRST TIMERS VS RETURNING VISITORS?
#############
#############

for the_date in sorted(total_people):
    for the_user in total_people[the_date]:
        if the_user not in already_added_commenters:
            if the_date not in new_commenters:
                new_commenters[the_date] = 1
            else:
                new_commenters[the_date] += 1
            already_added_commenters.append(the_user)
        else:
            if the_date not in returning_commenters:
                returning_commenters[the_date] = 1
            else:
                returning_commenters[the_date] += 1
                print the_date, the_user


#
starting_row += 10
title = "New Visitors adding " + types[:-3]
write_github_calendar(title, new_commenters, worksheet, starting_row, first_date, labels,
                                data_format, border_format, null_format, title_format, red_cond_format)


#
starting_row += 10
title = "Returning Visitors adding " + types[:-3]
write_github_calendar(title, returning_commenters, worksheet, starting_row, first_date, labels,
                                data_format, border_format, null_format, title_format, red_cond_format)




# this is the ratio of interactions to unique interactors
starting_row += 10
place_ratio = {}
for date in all_interactions:
    ratio = float(date_dict[date]) / float(all_interactions[date])
    if ratio == 1 and all_interactions[date] == 1: pass
    else:
        place_ratio[date] = ratio
title = "Ratio of (Unique Interactors/Total Interactions).             Darker = more diversity in the activity. lighter = more single-person activity "
write_github_calendar(title,
                        place_ratio, worksheet, starting_row, first_date, labels,
                        data_format, border_format, null_format, title_format, purp_cond_format)


# write out the totals for each type of submission

for typ in unique_submissions:
    starting_row += 10
    title = "Total " + typ + " per Day"
    date_dict = {}
    for date in unique_submissions[typ]:
        date_dict[date] = unique_submissions[typ][date][1]

    write_github_calendar(title, date_dict, worksheet, starting_row, first_date, labels,
                                    data_format, border_format, null_format, title_format, blue_cond_format)


###############################################################
activity = []
for hour in sorted(place_time):
    activity.append( [ hour, place_time[hour] ] )

print activity

###################################################################
###################################################################
# WRITE THE PLACE / TIME LINE AND BAR CHARTS
###################################################################
###################################################################

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.

###for dataset, worksheet in [[place_time, worksheet1]]:
row = 0
worksheet1.write_row(row, col, ['hr', 'places', 'comments', 'supports', 'other'])
row += 1
col = 0
for hour in sorted(place_time):
    worksheet1.write(row, col,     hour )
    worksheet1.write(row, col + 1, place_time[hour])
    worksheet1.write(row, col + 2, comment_time[hour])
    worksheet1.write(row, col + 3, support_time[hour])
    worksheet1.write(row, col + 4, other_time[hour])
    row += 1

worksheet2.write_row(0, 1, ['Sun','Mon', 'Tues', 'Wed', 'Thu', 'Fri', 'Sat'])
row = 1
worksheet2.write(row,0, "Adding Places")
worksheet2.write(row, 1, activity_by_day_of_week['Sun'])
worksheet2.write(row, 2, activity_by_day_of_week['Mon'])
worksheet2.write(row, 3, activity_by_day_of_week['Tue'])
worksheet2.write(row, 4, activity_by_day_of_week['Wed'])
worksheet2.write(row, 5, activity_by_day_of_week['Thu'])
worksheet2.write(row, 6, activity_by_day_of_week['Fri'])
worksheet2.write(row, 7, activity_by_day_of_week['Sat'])


for sub_typ in interaction_by_day_of_week:
    row += 1
    worksheet2.write(row, 0, sub_typ)
    worksheet2.write(row, 1, interaction_by_day_of_week[sub_typ]['Sun'])
    worksheet2.write(row, 2, interaction_by_day_of_week[sub_typ]['Mon'])
    worksheet2.write(row, 3, interaction_by_day_of_week[sub_typ]['Tue'])
    worksheet2.write(row, 4, interaction_by_day_of_week[sub_typ]['Wed'])
    worksheet2.write(row, 5, interaction_by_day_of_week[sub_typ]['Thu'])
    worksheet2.write(row, 6, interaction_by_day_of_week[sub_typ]['Fri'])
    worksheet2.write(row, 7, interaction_by_day_of_week[sub_typ]['Sat'])

day_of_week_chart = workbook.add_chart({'type': 'column'})
day_of_week_chart.set_title({
    'name': 'Map Activity by Day of Week',
    'name_font': {
        'name': 'Calibri',
    },
})
day_of_week_chart.add_series({
                    'values':     '=activity_dayofweek!B2:H2',
                    'categories': '=activity_dayofweek!B1:H1',
                    'name':             '=activity_dayofweek!A2',
                })
day_of_week_chart.add_series({
                    'values':     '=activity_dayofweek!B3:H3',
                    'categories': '=activity_dayofweek!B1:H1',
                    'name':             '=activity_dayofweek!A3',
                })
day_of_week_chart.add_series({
                    'values':     '=activity_dayofweek!B4:H4',
                    'categories': '=activity_dayofweek!B1:H1',
                    'name':             '=activity_dayofweek!A4',
                })
day_of_week_chart.add_series({
                    'values':     '=activity_dayofweek!B5:H5',
                    'categories': '=activity_dayofweek!B1:H1',
                    'name':             '=activity_dayofweek!A5',
                })




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
                    'line':           {'color': 'black'},
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

chart.add_series({
                    'values':     '=activity_hr!E2:E25',
                    'categories': '=activity_hr!A2:A25',
                    'line':           {'color': 'orange'},
                    'name':             'other',
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
worksheet_summary.insert_chart('B17', day_of_week_chart)

workbook.close()