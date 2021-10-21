import argparse
import csv
import requests
import json
import logging

"""Example program for STC. He was interested
in having a report/database of email stats.  This app built
that database content."""

# Ugly global data.
entryCache = []

def increment(data, field, key):
    """Bump the count for `key` in the `field` dict in `data`.
    If `key` is not there, then it's added and set to 1.
    Parameters:
        data    Data object to update
        field   Field field in `d`
        key     key in the `field` dict
    """
    pile = data[field]
    if key not in pile:
        pile[key] = 0
    pile[key] = pile[key] + 1


def incrementIfTrue(data, field, value):
    """Bump the count for `field` in `data` if `value` is true.

    Parameters:
        data    Data object to update
        field   Field field in data
        value   Boolean
    """
    if value:
        data[field] = data[field] + 1


def increase(data, field, amount):
    """ Adds `amount` to the count for the `field` dict in `data`.
    Note that no attempt is used to qualify `field`.  A exception
    will be thrown if that happens.

    Parameters:
        data    Data object to update
        field   Field field in data
        amount  Value to add. Is a string.
    """
    data[field] = data[field] + int(amount)


def updateStats(r, stats):
    """Update a stats object using the provided recipient
    record.  This method only updates these fields:
    * opened
    * clicked
    * converted
    * unsubscribed
    * numberOfLinksClicked
    * conversions

    The remaining fields are only updated by oneRecipient.

    Parameters:
        r       Recipient record
        stats   Stats record to update

    Returns
        updated stats record
    """

    increase(stats, 'recipients', 1)

    for key in ['status', 'splitName']:
        # Kludge to keep blast-level stats and allow 'status'
        # and 'splitName' to populate their own stats objects.
        increment(stats, key, r[key])
    for key in ['opened', 'clicked', 'converted', 'unsubscribed']:
        incrementIfTrue(stats, key, r[key])
    for key in ['numberOfLinksClicked']:
        increase(stats, key, r[key])
    # Not all clicks are conversions.  Engage lets us
    # know the places that really were conversions.
    if "conversionData" in r.keys():
        for conversion in r['conversionData']:
            increment(stats, 'conversion', conversion['activityName'])

    return stats


def handleDomain(r, data):
    """Update the domain data in `data` using the provided
    recipient record.

    Parameters:
        r       Recipient record
        data    Data record to update

    Returns:
        returns the updated data record
    """

    if 'supporterEmail' in r.keys():
        key = r['supporterEmail'].split("@")[1]
        if key not in data['domain'].keys():
            data['domain'][key] = newStats()
        updateStats(r, data['domain'][key])
    return data


def handleSplit(r, data):
    """Update the split data in `data` using the provided
    recipient record.

    Parameters:
        r       Recipient record
        data    Data record to update

    Returns:
        returns the updated data record
    """

    key = ""
    if 'splitName' in r.keys():
        key = r['splitName']
    if key not in data['splitName'].keys():
        data['splitName'][key] = newStats()
    updateStats(r, data['splitName'][key])
    return data


def handleStatus(r, data):
    """Update the status data in `data` using the provided
    recipient record.

    Parameters:
        r       Recipient record
        data    Data record to update

    Returns:
        returns the updated data record
    """

    key = ""
    if 'status' in r.keys():
        key = r['status']
    if key not in data['status'].keys():
        data['status'][key] = newStats()
    updateStats(r, data['status'][key])
    return data


def oneRecipient(r, data):
    """Process the contents of a single recipient field.
    Use `data` to tabulate the results.

    Parameters:
        r      Recipient record
        data    Data object to update
    """

    try:
        updateStats(r, data)
    except TypeError:
        print("Type error on data {data}")
    handleDomain(r, data)
    handleSplit(r, data)
    handleStatus(r, data)


def handleRecipients(recipientsData, data):
    """Process the list of recipients in this individual email entry.

    Parameters:
        recipientsData  Dict containing list of recipients
        data            Accumulate here
    """
    count = int(recipientsData['total'])
    logging.info(
        f"scanEmail: adding {count:>4} recipients, {data['recipients']:>6} total")
    if count > 0:
        for r in recipientsData['recipients']:
            oneRecipient(r, data)
    return count


def handlePayload(rPayload, dPayload, data):
    """Handle one payload of individualEmailActivityData.
    Note that we are retrieving for only one email blast, but
    the API returns the results returns an array.  The array always
    contains one item.  A warning message goes to the console if
    there are more than one items in the array.

    Parameters:
        rPayload    Request payload.  Passed here so that we can update `cursor`.
        dPayload    Payload containing individualEmailActivityData
        data        Accunulate into this

    Returns:
        The number of recipients added from this payload, or
        zero to indicate end-of-data.
    """
    a = dPayload['individualEmailActivityData']
    count = 0
    if len(a) > 1:
        logging.warn(
            f"scanEmail: payload unexpectedly contains {len(a)} individual email activities")
    for entry in a:
        name = "none"
        if 'name' in entry.keys():
            name = entry['name']

        # Going back to Engage returns email information.  We'll
        # use a global dict as cache so that we won't display
        # the same blast name more than once.
        if entry['id'] not in entryCache:
            logging.info(f"scanEmail: entry  {entry['id']}")
            logging.info(f"scanEmail: name   {name}")
            entryCache.append(entry['id'])
        recipientsData = entry['recipientsData']
        count = handleRecipients(recipientsData, data)

        # Transfer the cursor from this payload to the request payload.
        # The cursor does a really nice job of pagination.  If this is
        # an edge condition (blast without a cursor because there's no
        # data), then we return a zero. That indicates end-of-data.
        #
        # Note: if there are every two entries in individualEmailActivityData,
        # then the cursor could possibly fail. We'll implode that bridge
        # if we every get there...
        if 'cursor' in entry.keys():
            rPayload['cursor'] = entry['cursor']
    return count


def scanEmail(token, emailID, type, data):
    """Scan an email blast.  Tabulate blast and recipient stats
    into `data`.

    Parameters:
        token       Engage Integration API token
        emailID     UUID of the email to scan
        type        see `payloadTypes` (above)
        data        Tabulate here.

    Errors:
        An invalid email type is noisily fatal.
        HTTP errors are also noisily fatal.
    """

    searchURL = 'https://api.salsalabs.org/api/integration/ext/v1/emails/individualResults'

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
            "count": 20,
            "type": "EMAIL",
            "id": emailID
        }
    }

    # Nominal record count to kick off the processing loop.
    count = 1

    # We need the request payload so that it can be updated with a
    # `cursor` field.
    rPayload = params['payload']

    # This loop uses the `cursor` from the response payload to manage
    # pagination.  Much easier than using count/total.  Just keep going
    # no recipients are returned from a read...
    while count > 0:
        r = requests.post(searchURL, headers=headers, data=json.dumps(params))
        if (r.status_code != 200):
            logging.fatal(
                f"{rPayload['type']}: HTTP status code {r.status_code}")
            logging.fatal(r.text)
            exit(1)
        dPayload = r.json()['payload']
        count = handlePayload(rPayload, dPayload, data)


def newStats():
    """Allocate and initialize an new stats object.

    Returns:
        Status array for tabulation."""

    return {
        'emailID': None,
        'type': None,
        'recipients': 0,
        'opened': 0,
        'clicked': 0,
        'converted': 0,
        'unsubscribed': 0,
        'numberOfLinksClicked': 0,
        'conversion': {},
        'domain': {},
        'splitName': {},
        'status': {},
        'blast_status': {},
        'blast_splitName': {}
    }


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
    parser.add_argument('--emailID', action="store", required=True,
                        help=f"email UUID.")
    parser.add_argument('--emailType', action="store",
                        default="EMAIL", choices=payloadTypes)
    parser.add_argument("--output", action="store", default="blast_statistics.json",
                        help="write JSON results into this file")

    args = parser.parse_args()
    if len(args.emailType) == 0:
        logging.fatal(
            f"Error: --emailType is required. Choose from {payloadTypes}.")
        exit(1)
    # if args.emailType not in payloadTypes:
    #     logging.fatal(f"Error: '{args.emailType}' is not a valid payload type.  Choose from {payloadTypes}.")
    #     exit(1)

    if len(args.output) == 0:
        logging.fatal(
            f"Error: --output is required. Provide an output filename.")
        exit(1)

    data = newStats()

    # Process all recipients in the email blast. Tabulate into `data`.
    scanEmail(args.token, args.emailID, args.emailType, data)

    # Sort the domains by the number of recipients.
    domains = data['domain']
    domains = {key: value for key, value in reversed(
        sorted(domains.items(), key=lambda item: item[1]["recipients"]))}
    data['domain'] = domains

    # Write to a disk file.
    with open(args.output, 'w') as f:
        f.write(json.dumps(data, indent=4))
        f.close()
    logging.info(f"main: Done. Results can be found in {args.output}.")


if __name__ == '__main__':
    main()
