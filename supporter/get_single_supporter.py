import argparse
import csv
import requests
import json
import logging

"""See the JSON for a supporter using Python3 and no utility classes."""

def readSupporter(token, supporterID):
    """Read a supporter.  Display JSON.

    Parameters:
        token       Engage Integration API token
        supporterID UUID of the email to scan

    Errors:
        An invalid email type is noisily fatal.
        HTTP errors are also noisily fatal.
    """

    searchURL = 'https://api.salsalabs.org/api/integration/ext/v1/supporters/search'

    # HTTP headers to send the API token.
    headers = {
        'authToken': token,
        'content-type': 'application/json'
    }

    # Payload for the POST.
    # All of the unnecessary parameters have been strippped out.
    # This works really well for the one UUID that we can specify.
    params = {
        "payload": {
            "identifiers": [ supporterID ],
            "identifierType": "SUPPORTER_ID",
            "count": 20,
            "offset": 0
        }
    }
    r = requests.post(searchURL, headers=headers, data=json.dumps(params))
    if (r.status_code != 200):
        logging.fatal(f"error: HTTP status code {r.status_code}")
        logging.fatal(r.text)
        exit(1)
    dPayload = r.json()['payload']
    print (json.dumps(dPayload, indent=4))

def main():
    """Program entry point. Uses a user-provided email UUID to retrieve
    blast and recipient statistics. Tabulates into an internal dictionary.
    Writes the dictionary as JSON to to a user-provided filename."""

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    # Payload types used for validation.
    payloadTypes = [
        "EMAIL",
        "COMM_SERIES"]

    parser = argparse.ArgumentParser(
        description='Tabulate statistics for a single Engage blast')
    parser.add_argument('--token', action='store', required=True,
                        help='Engage Integration API token')
    parser.add_argument('--supporterID', action="store", required=True,
                        help=f"supporterID.")

    args = parser.parse_args()
    readSupporter(args.token, args.supporterID)

if (__name__) == "__main__":
    main()

