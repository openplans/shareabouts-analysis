import requests
from requests.auth import HTTPBasicAuth
import settings



from time import sleep
import time



def get_data(URL, retries=5):
    """   go to the URL and return the JSON using UN/PW credentials  """
    from time import sleep
    import settings

    try:
        print settings.PASSWORD
        r = requests.get(URL, auth=HTTPBasicAuth(settings.USERNAME, settings.PASSWORD))
    except Exception as e:
        print 'Something went wrong: %s - %s\r' % (type(e).__name__, e),
    else:
        if r.status_code == 200:
            return r.json()
        else:
            print 'Got an unexpected %s response: %s\r' % (r.status_code, r.text),

    if retries > 0:
        time.sleep(1)
        return get_data(URL, retries - 1)
    else:
        print '\nNo more retries for URL "%s".' % (URL,)
        sys.exit(1)


def pull_dataset_data(JSON, data_node):
    """ handles pagination. dump the data into a list,
        and repeat if there's another page   """
    results = []
    while JSON["metadata"]["next"] is not None:     # if there's another page
        for item in JSON[data_node]:
            results.append(item)
        JSON = get_data(JSON["metadata"]["next"])
    for item in JSON[data_node]:  # dump the data one more time for the final page
        results.append(item)
    return results



def history_of_dataset(PLACES_URL):
    """ identifies the first and last date that places
        were added to the dataset """
    print PLACES_URL
    JSON = get_data(PLACES_URL)
    # change the cutoff number to prevent large datasets from being processed
    if JSON["metadata"]["length"] > 5:
        return None, None
    else:
        all_places = pull_dataset_data(JSON, "features")
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
            return None, None

def pull_relevant_data(JSON):
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

        first_point, last_point = None, None #history_of_dataset(dataset["places"]["url"])

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







data_url = 'http://data.shareabouts.org/api/v2/~/datasets?format=json&page=1'

data_server = get_data(data_url)