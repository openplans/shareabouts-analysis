import xlsxwriter

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('testing.xlsx')
worksheet1 = workbook.add_worksheet( "place_time" )
worksheet2 = workbook.add_worksheet( "comment_time" )
worksheet3 = workbook.add_worksheet( "support_time" )
worksheet_summary = workbook.add_worksheet( "SUMMARY" )

place_time = {'00': 4,
             '01': 4,
             '02': 4,
             '03': 4,
             '04': 9,
             '05': 1,
             '06': 0,
             '07': 1,
             '08': 2,
             '09': 1,
             '10': 1,
             '11': 4,
             '12': 3,
             '13': 21,
             '14': 10,
             '15': 11,
             '16': 21,
             '17': 49,
             '18': 12,
             '19': 5,
             '20': 11,
             '21': 10,
             '22': 11,
             '23': 49}


comment_time = {'00': 9,
                 '01': 5,
                 '02': 0,
                 '03': 0,
                 '04': 0,
                 '05': 1,
                 '06': 0,
                 '07': 0,
                 '08': 0,
                 '09': 0,
                 '10': 2,
                 '11': 1,
                 '12': 5,
                 '13': 18,
                 '14': 11,
                 '15': 21,
                 '16': 13,
                 '17': 7,
                 '18': 9,
                 '19': 9,
                 '20': 10,
                 '21': 11,
                 '22': 12,
                 '23': 4}

support_time = {'00': 29,
                     '01': 48,
                     '02': 59,
                     '03': 39,
                     '04': 28,
                     '05': 29,
                     '06': 0,
                     '07': 1,
                     '08': 1,
                     '09': 0,
                     '10': 0,
                     '11': 30,
                     '12': 43,
                     '13': 26,
                     '14': 48,
                     '15': 63,
                     '16': 111,
                     '17': 138,
                     '18': 31,
                     '19': 128,
                     '20': 46,
                     '21': 53,
                     '22': 21,
                     '23': 52}

activity = []
for hour in sorted(place_time):
    activity.append( [ hour, place_time[hour] ] )

print activity
# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.

for dataset, worksheet in [[place_time, worksheet1],[comment_time, worksheet2],[support_time, worksheet3]]:
    row = 0
    col = 0
    for hour in sorted(dataset):
        worksheet.write(row, col,     hour )
        worksheet.write(row, col + 1, dataset[hour])
        row += 1


# chart time
chart = workbook.add_chart({'type': 'line'})
chart.add_series({
                    'values':     '=place_time!B1:B24',
                    'categories': '=place_time!A1:A24',
                    'line':           {'color': 'red'},
                    'name':             'places added',
                })

chart.add_series({
                    'values':     '=comment_time!B1:B24',
                    'categories': '=comment_time!A1:A24',
                    'line':           {'color': 'green'},
                    'name':             'comments',
                })

chart.add_series({
                    'values':     '=support_time!B1:B24',
                    'categories': '=support_time!A1:A24',
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


worksheet_summary.insert_chart('A5', chart)

### Write a total using a formula.
###worksheet.write(row, 0, 'Total')
###worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()