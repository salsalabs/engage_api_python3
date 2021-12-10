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

def dumpJSON(x):
    """
    Generic function to return 'x' in formatted JSON.
    
    Parameters:
    
        x   any     thing to see
    
    Returns:

        String containing 'x' as formatted JSON
    """
    return json.dumps(x, indent=4)

def field(s, n, d):
    """
    Engage does not put empty fields into the JSON from API calls.
    That means we need to be careful when try to get fields from a
    dict parsed from JSON provided by Engage.  
    
    This function checks to see if a field ('n') is in a dict ('s').
    If the answer is yes, then the value is returned.  If no, then
    'd' is returned. """ 

    if n in s:
        return s[n]
    else:
        return d

def firstEmail(m, d):
    """
    Engage stores emails and phone numbers in the 'contacts' section
    of a supporter record.  This function finds the first email.  If
    there's not an email record, then we'll return a None.
    
    Parameters:

        m   dict    supporter record
        d   string  default value if an email is not equipped
    
    Returns:

        string containing an email address, or
        None if no email is configured
    """

    if 'contacts' not in m:
        return d
    for c in m['contacts']:
        if c['type'] == 'EMAIL':
            return c['value']
    return d


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
            s = dumpJSON(json.loads(r.text))
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
    seeSegment(args)

    # offset = 0
    # count = args.count
    endpoint = 'https://api.salsalabs.org/api/integration/ext/v1/segments/members/search'
    requestPayload = {
        "payload": {
            "segmentId": args.segment_id,
            "offset": 0,
            "count": args.count
        }
    }
    while requestPayload['payload']['count'] == args.count:
        response = postEngage(args, endpoint, requestPayload)

        payload = response["payload"]
        total = field(payload, 'total', '(None)')
        offset = field(payload, 'offset', requestPayload['payload']['offset'])
        count = field(payload, 'count', '(None)')
        logging.info(f"{offset}/{total} {count} records")

        supporters = field(payload, 'supporters', None)
        if supporters is None:
            logging.warning("The segment does not have any members")
            exit(1)
        showMembers(supporters)
        requestPayload['payload']['offset'] += count
        requestPayload['payload']['count'] = count

def seeSegment(args):
    """
    Display the segment for 'segment-id' in the command-line argments.

    Parameters:

        args    dict    command-line arguments
    
    Errors:

        Python errors are noisily fatal.
        HTTP errors are noisily fatal.
    """
    endpoint = 'https://api.salsalabs.org/api/integration/ext/v1/segments/search'
    payload = {
        "payload": {
            "identifiers": [ args.segment_id],
            "identifierType": "SEGMENT_ID"
        }
    }
    response = postEngage(args, endpoint, payload)

    # Extract the segments from the response payload.
    payload = response["payload"]
    segments = payload["segments"]

    # Handle each segment. Okay, so there's just one, but we're
    # iterating anyway...
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

    # Engage does not include fields in the payload if
    # they are empty in the database.
    name = field(s, 'name', '(None)')
    totalMembers = field(s, 'totalMembers', '(None)')
    showCommon(s, f"{name:50} {totalMembers:>7}")

def showMembers(members):
    """
    Show members as indented data.  Minimal info -- this is just a demo.
    
    Parameters:

        members     list of dict    Supporter records for group members
    
    Errors:

        Python errors are noisy and fatal

    """
    for m in members:
        supporterID = m['supporterId']
        firstName = field(m, 'firstName', '')
        lastName = field(m, 'lastName', '')
        email = firstEmail(m, '(None)')
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
