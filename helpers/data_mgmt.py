import csv
import os
import datetime

def write_csv(OUTPUT_FILE, HEADER, DATA):
    with open(OUTPUT_FILE, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(HEADER)
        for item in DATA:
            writer.writerow(DATA[item])
    print "Wrote file to %s" % OUTPUT_FILE

def get_day_of_week(DATE):
    """ turns a date into a string, as day of week, like 'Sun'   """
    the_date = datetime.datetime.strptime(DATE, '%Y-%m-%d')
    return the_date.strftime('%a')

def combine_datasets(DATA_LIST, OUTPUT_DICT):
    """  toss datasets into a dictionary.
         if it's already in in dictionary, use the one with more points or comments """
    for item in DATA_LIST:
        unique_id = os.path.join(item[0], item[3]) # owner/slug
        # if the dataset is missing from the list, add it
        if unique_id not in OUTPUT_DICT:
            OUTPUT_DICT[unique_id] = item
        # if it's already in the list, use the one with more places
        else:
            new_case = item[5].split(".shareabouts.org")[0]
            existing_case = OUTPUT_DICT[unique_id][5].split(".shareabouts.org")[0]
            # PLACES
            if item[4] > OUTPUT_DICT[unique_id][4]:
                OUTPUT_DICT[unique_id] = item
            elif item[4] < OUTPUT_DICT[unique_id][4]:
                pass
            # if they have the same number of points, check comments
            else:
                # use the new one if it has more comments
                # COMMENTS
                if item[6] > OUTPUT_DICT[unique_id][6]:
                    OUTPUT_DICT[unique_id] = item
                else:
                    pass