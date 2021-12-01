import argparse
import csv
import requests
import json
import logging

"""See the JSON for one activity using Python3 and no utility classes."""


def readActivity(token, identifierType, id, summary):
    """Read a activity.  Display JSON.

    Parameters:
        token           Engage Integration API token
        identifierType One of the valid indentifer types types:
                        "TRANSACTION_ID",
                        "TEMPLATE_ID",
                        "ACTIVITY_FORM_ID",
                        "SUPPORTER_ID"
        id              ID to use for search
        summary         True for basic activity information.
                        Useful for supporters and forms.

    Errors:
        HTTP errors are also noisily fatal.
        Engage-specific errors are also noisily fatal.
    """

    searchURL = 'https://api.salsalabs.org/api/integration/ext/v1/activities/search'

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
            "activityFormIds": [id],
            "type": identifierType,
            "count": 20,
            "offset": 0
        }
    }
    logging.info(f"Searching activitys for {identifierType} {id}")
    r = requests.post(searchURL, headers=headers, data=json.dumps(params))
    if (r.status_code != 200):
        logging.fatal(f"error: HTTP status code {r.status_code}")
        logging.fatal(json.dumps(json.loads(r.text), indent=4))
        exit(1)
    response = r.json()
    if "errors" in response.keys():
        logging.fatal("Read errors:")
        logging.fatal(json.dumps(response['errors'], indent=4))
    dPayload = r.json()['payload']
    if summary:
        activitys = dPayload['activities']
        logging.info(f"{'Activity ID':<36}  {'Activity Date':<24}  {'Activity Type':<16}  {'TrackingCode'}")
        for r in activitys:
            if r['result'] == 'FOUND':
                logging.info(f"{r['activityId']}  {r['activityDate']}  {r['activityType']:<16}  {r['trackingCode']}")
            else:
                logging.info("No matching trasactions found")
    else:
        logging.info(f"Results:\n{json.dumps(dPayload, indent=4)}")


def main():
    """Program entry point. Uses a user-provided id, retrieves
    activities and outputs JSON to the console."""

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    validActivityTypes = ["SUBSCRIPTION_MANAGEMENT",
                          "SUBSCRIBE",
                          "FUNDRAISE",
                          "PETITION",
                          "TARGETED_LETTER",
                          "REGULATION_COMMENTS",
                          "TICKETED_EVENT",
                          "P2P_EVENT",
                          "FACEBOOK_AD"]

    parser = argparse.ArgumentParser(
        description='Search for one activity')
    parser.add_argument('--token', action='store', required=True,
                        help='Engage Integration API token')
    parser.add_argument('--identifierType', choices=validActivityTypes,
                        default="SUBSCRIBE",
                        help="Search for this identifier type")
    parser.add_argument('--id', action="store", required=True,
                        help="ID to use for searching")
    parser.add_argument('--summary', action="store_true",
                        help="Only show basic activity information")

    args = parser.parse_args()
    readActivity(args.token, args.identifierType, args.id, args.summary)


if (__name__) == "__main__":
    main()
