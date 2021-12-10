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

def field(s, n, d):
    """
    Engage does not equip JSON with empty fields. That means we need
    to be careful when try to get fields from a dict parsed from JSON
    provided by Engage.  
    
    This function checks to see if a field ('n') is in a dict ('s').
    If the answer is yes, then the value is returned.  If no, then
    'd' is returned. """ 

    if n in s:
        return s[n]
    else:
        return d

def getSegment(args):
    """
    Retrieves the segment for 'segment-id' in args. 

    Parameters:

        args    dict    command-line arguments.

    Returns:

        Returns a segment object if the segment-id is valid.
        Returns None otherwise
    
    Errors:

        Python errors are noisily fatal.
        HTTP errors are noisily fatal.
    """
    endpoint = 'https://api.salsalabs.org/api/integration/ext/v1/segments/search'
     # Specify the segment ID to read.
    payload = {
        "payload": {
            "identifiers": [ args.segment_id],
            "identifierType": "SEGMENT_ID"
        }
    }
    response = postEngage(args, endpoint, payload)
    print(json.dumps(response, indent=4))

    # Extract the segments from the response payload.
    rPayload = response["payload"]
    segments =  rPayload["segments"]

    # Handle each segment. Okay, so there's just one, but we're
    # iterating the list anyway...
    for s in segments:
        if "errors" in s:
            showErrors(s)
        elif "warnings" in s:
            showWarnings(s)
        else:
            showContent(s)

def postEngage(args, endpoint, payload):
    """
    Function to POST the payload to the endpoint and return
    the response buffer.  Errors are noisy and fatal.

    Parameters:

        args        dict    command-line arguments
        endpoint    string  Engage API URL
        payload     dict    Payload to submit in the POST body

    Returns:

        Returns the response object
    
    Errors:

        Python errors are noisily fatal.
        HTTP errors are noisily fatal.

    """
    # HTTP headers to send the API token.
    headers = {
        'authToken': args.token,
        'content-type': 'application/json'
    }
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
    return r.json()

def run(args):
    """ Submit the list of segment IDs to Engage.  Display the results.


    Parameters:
        args    dict    Commnd line arguments. Contains

                        token        string  Engage Integration API token
                        segment_id   string  Comma-separated segment IDs
                        count        int     Number of records per call
    Errors:
        HTTP errors are also noisily fatal.
        Engage-specific errors are also noisily fatal.
    """

    # offset = 0
    # count = args.count
    endpoint = 'https://api.salsalabs.org/api/integration/ext/v1/segments/members/search'
    
    segment = getSegment(args)
    if segment is None:
        return

    # Specify the segment ID list and the type.
    payload = {
        "payload": {
            "segmentId": args.segment_id,
            "offset": 0,
            "count": args.count
        }
    }

    # Process supporters from the payload
    rPayload = response["payload"]
    segments =  rPayload["segments"]

    # Handle each segment.
    for s in segments:
        if "errors" in s:
            showErrors(s)
        elif "warnings" in s:
            showWarnings(s)
        else:
            showContent(s)
            showMembers(s)

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

    # Engage does not include fields in the payload if
    # they are empty in the database.
    name = field(s, 'name', '(None)')
    totalMembers = field(s, 'totalMembers', '(None)')
    showCommon(s, f"{name:50} {totalMembers:>7}")

def showMembers(s):
    """
    Show members as indented data.  Minimal info -- this is just a demo.
    
    Parameters:

        s       dict      Segment object
    
    Errors:

        Python errors are noisy and fatal

    """
    if "supporters" not in s:
        showCommon(s, "Segment has no members")
        return
    a = s["supporters"]
    logging.info(f"    Segment has {len(a)} supporters.")
    for supporter in a:
        supporterID = s['supporterID']
        firstName = field(s, 'firstName', "")
        lastName = field(s, 'lastName')
        email = "email@example.org" #firstEmail(s)
        logging.info(f"{supporterID} {firstName:<20} {lastName:<20} {email}")

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
    parser.add_argument('--segment-id', action="store", required=True,
                        help="Segment ID of interest")

    args = parser.parse_args()
    run(args)


if (__name__) == "__main__":
    main()
