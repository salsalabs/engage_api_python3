# Application to display email blast info including id, name, title and URL.
# You provide the Engage Website Developer API token.
# You (optionally) provide a host.  If no host is provided, then this app uses
# the Engage Website Develoepr API host.

import argparse
import csv
import json
import os
import sys
import yaml

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from pkg.net import EngageNet

# Parameters required by the API endpoint.
request = {
    'payload': {
        #'criteria':   None,            # String     optional     A string representing full or partial name/description
        'sortField':  'name',           # String     optional     sort field name. Supported values: "name", "description"
        'sortOrder':  'ASCENDING',      # String     optional     sort order. Values: ASCENDING/DESCENDING
        'count':      10,               # Integer    optional     number of results to be returned. Max = 25. Default = 10
        'offset':     0,                # Integer    optional     records offset. Used for pagination
        #'startDate':  None,            # Date       optional     Means "from date". Blast created on or after specified dateformat: 2018-01-08T23:01:18.000Z
        #'endDate':    None,            # Date       optional     Means "to date". Blast created on or after specified dateformat: 2018-01-08T23:01:18.000Z
    }
}

parser = argparse.ArgumentParser(description='Display email blast URLs for Engage')
parser.add_argument('--login', dest='loginFile', action='store',
                            help='YAML file with login credentials')

args = parser.parse_args()
if args.loginFile == None:
    print("Error: --login is REQUIRED.")
    exit(1)
cred = yaml.load(open(args.loginFile))

devHost = 'dev-api.salsalabs.org'
if 'devHost' in cred:
    host = cred['devHost']

# Parameters for EngageNet
params = {
    "endpoint": "/api/developer/ext/v1/blasts",
    'host': devHost,
    'token': cred['devToken'],
    'method': 'GET',
    'request': request
}

with open('email_blast_urls.csv', 'w') as csvfile:
    w = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    headers = 'id,name,title,subject,hasUrl,url'.split(',')
    w.writerow(headers)

    request_payload = request['payload']
    count = request_payload['count']
    while count > 0:
            net = EngageNet(**params)
            response = net.run()
            payload = response['payload']
            total = int(payload['total'])
            count = int(payload['count'])
            print(f"Count is {count}, total is {total}")
            if 'results' not in payload:
                break
            results = payload['results']
            for r in results:
                content = r['content']
                for c in content:
                    if 'webVersionEnabled' in c and c['webVersionEnabled']:
                        id = r['id']
                        name = r['name']
                        title = c['pageTitle']
                        subject = c['subject']
                        hasUrl = str(c['webVersionEnabled'])
                        try:
                            url = c['pageUrl']
                        except KeyError as e:
                            print("Error ", e, " extracting URL from content")
                            print("\n", c, "\n\n")
                            url = None
                        if url != None:
                            row = [
                                id,
                                name,
                                title,
                                subject,
                                hasUrl,
                                url
                            ]
                            w.writerow(row)
            net.request['payload']['offset'] = net.request['payload']['offset'] + count
            print(json.dumps(net.request['payload'], indent=4))
            print('{0:3}/{1:3}'.format(request_payload['offset'], total))

    csvfile.close()
    print("Output may be found in email_blasts_urls.csv")
    sys.exit(0)
