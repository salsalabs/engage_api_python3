import argparse
import csv
import requests
import json
import logging

"""
Standalone app to retrieve segments and member counts from the Engage
API.  The user provides the Engage token and a comma-separated list
of segment IDs.  The output is a simple list of ID, segment and count.
"""

def run(args):
    """ Submit the list of segment IDs to Engage.  Display the results.


    Parameters:
        args    dict    Commnd line arguments. Contains

                        token   string  Engage Integration API token
                        ids     string  Comma-separated segment IDs
                        count   int     Number of records per call
    Errors:
        HTTP errors are also noisily fatal.
        Engage-specific errors are also noisily fatal.
    """

    segmentIDs = args.ids.split(",")
    # offset = 0
    # count = args.count
    endpoint = 'https://api.salsalabs.org/api/integration/ext/v1/segments/search'
    
    # HTTP headers to send the API token.
    headers = {
        'authToken': args.token,
        'content-type': 'application/json'
    }

    payload = {
        "payload": {
            "identifiers": segmentIDs,
            "identifierType": "SEGMENT_ID"
        }
    }

    #while count > 0:
    # TODO: Report this as a bug. In the doc, but we see 
    #    payload['offset'] = offset
    #    payload['count'] = count
    # {"payload": {"identifiers": ["2828b7f0-f2cf-455b-bcbe-7a1fa466978f"], "identifierType": "SEGMENT_ID", "includeSegmentCounts": true}, "count": 20}
    # 2021-12-03 11:26:59,902 error: HTTP status code 400
    # 2021-12-03 11:26:59,902 Unrecognized field &quot;count&quot; (class com.salsalabs.ignite.hq.api.model.integration.ext_v1.APIIntegrationRequest), not marked as ignorable

    # Somewhere, there's a presumption that the list of segments will be shorter
    # that the maximum batch count.  TODO: Study.
    body = json.dumps(payload)
    r = requests.post(endpoint, headers = headers, data = body)

    if (r.status_code != 200):
        logging.fatal(f"error: HTTP status code {r.status_code}")
        try:
            s = json.dumps(json.loads(r.text), indent=4)
        except:
            s = r.text
        logging.fatal(s)
        exit(1)
    response = r.json()
#    count = response['count']

#   if count > 0:
    dPayload = response["payload"]
    segments =  dPayload["segments"]
    for s in segments:
        if "errors" in s:
            showErrors(s)
        elif "warnings" in s:
            showWarnings(s)
        else:
            showContent(s)

   
def showErrors(s):
    """ Display segment-level errors."""
    for e in s['errors']:
        showCommon(s, f"{e['message']} ({e['code']})")

def showWarnings(s):
    """ Display segment-level warnings."""
    for e in s['warnings']:
        showCommon(s, f"{e['message']} ({e['code']})")

def showCommon(s, t):
    """ Output text in a common format.

    Parameters:

        s       dict    Segment record
        t       string  Text to display
    """
    print(f"{s['segmentId']} {t}")

def showContent(s):
    """ Display segment ID, name and count."""
    if "name" in s:
        name = s["name"]
    else:
        name = "(None)"
    if "totalMembers" in s:
        totalMembers = s["totalMembers"]
    else:
        totalMembers = "(None)"

    showCommon(s, f"{name:50} {totalMembers:>7}")
 
def main():
    """
    Program starts here.  Errors are noisily fatal.
    """
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
 
    parser = argparse.ArgumentParser(
        description='Search for segments by segmentIDs')
    parser.add_argument('--token', action='store', required=True,
                        help='Engage Integration API token')
    parser.add_argument('--count', type=int, default=20,
                        help="Records per call.  Typically 20...")
    parser.add_argument('--ids', action="store", required=True,
                        help="Comma-separated list of segment ID(s) to use.")

    args = parser.parse_args()
    run(args)


if (__name__) == "__main__":
    main()
