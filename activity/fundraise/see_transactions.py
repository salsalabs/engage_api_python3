import argparse
import csv
import requests
import json
import logging

"""
Standalone app to see the JSON for a transactions. The
user chooses an ID and an ID type.  The app displays
JSON.  Using --summary creates a single-line summary for 
each transaction.

This is an API demo.  The app just shows the first 20
transactions.
"""

def readTransaction(token, identifierType, id, summary):
    """Read a transaction.  Display JSON or a single-line summary.

    Parameters:
        token           Engage Integration API token
        identifierType  One of the valid indentifer types types:
                        "TRANSACTION_ID",
                        "TEMPLATE_ID",
                        "ACTIVITY_FORM_ID", or
                        "SUPPORTER_ID"
        id              ID to use for search
        summary         True for basic transaction information.
                        Useful for supporters and forms.

    Errors:
        HTTP errors are also noisily fatal.
        Engage-specific errors are also noisily fatal.
    """

    searchURL = 'https://api.salsalabs.org/api/integration/ext/v1/transactionDetails/search'

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
            "identifiers": [id],
            "identifierType": identifierType,
            "count": 20,
            "offset": 0
        }
    }
    logging.info(f"Searching transactions for {identifierType} {id}")
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
        transactions = dPayload['transactions']
        logging.info(f"{'Transaction ID':<36}  {'Transaction Date':<24}  {'Transaction Type':<16}  {'Amount':>7}")
        for r in transactions:
            if r['result'] == 'FOUND':
                logging.info(f"{r['transactionId']}  {r['transactionDate']}  {r['transactionType']:<16}  {r['amount']:7.2f}")
            else:
                logging.info("No matching trasactions found")
    else:
        logging.info(f"Results:\n{json.dumps(dPayload, indent=4)}")


def main():
    """Program entry point. Uses a user-provided id, retrieves
    the transaction and outputs JSON to the console."""

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    validTransactionTypes = ["TRANSACTION_ID",
                             "TEMPLATE_ID",
                             "ACTIVITY_FORM_ID",
                             "SUPPORTER_ID"]

    parser = argparse.ArgumentParser(
        description='Search for transactions by identifier')
    parser.add_argument('--token', action='store', required=True,
                        help='Engage Integration API token')
    parser.add_argument('--identifierType', choices=validTransactionTypes,
                        default="TRANSACTION_ID",
                        help="Search for this identifier type")
    parser.add_argument('--id', action="store", required=True,
                        help="ID to use for searching")
    parser.add_argument('--summary', action="store_true",
                        help="Only show basic transaction information")

    args = parser.parse_args()
    readTransaction(args.token, args.identifierType, args.id, args.summary)


if (__name__) == "__main__":
    main()
