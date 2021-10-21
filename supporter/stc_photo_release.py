import requests
import json
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
token = ''

# Search for activities that reference the photo release custom field.

host = 'https://api.salsalabs.org'
cmd = '/api/integration/ext/v1/activities/search'
url = f'{host}{cmd}'

headers = {
	'authToken': token,
	'content-type': 'application/json'
}
payloadTypes = [
#	"SUBSCRIPTION_MANAGEMENT",
#	"SUBSCRIBE",
#	"FUNDRAISE",
	"PETITION",
#	"TARGETED_LETTER",
	"REGULATION_COMMENTS",
	"TICKETED_EVENT",
	"P2P_EVENT",
	"FACEBOOK_AD"]

for payloadType in payloadTypes:
	rPayload =  {
	      	'type': payloadType,
	       	'modifiedFrom':'2019-06-30T14:09:58.307Z',
	       	'offset': 0,
	       	'count': 20
   	}
	while rPayload['count'] == 20:
		payload = { 'payload': rPayload }
		r = requests.post(url, headers=headers, data=json.dumps(payload))
		if (r.status_code != 200):
			logging.fatal(f"{rPayload['type']}: HTTP status code {r.status_code}")
			exit(1)
		if rPayload['offset'] % 1000 == 0:
			logging.info(f"{rPayload['type']}: Offset is {rPayload['offset']}, count is {rPayload['count']}")
		dPayload = r.json()
		results = dPayload['payload']
		count = results['count']

		for a in results['activities']:
			if len(a['customFieldValues']) > 0:
				value = list(c['value'] for c in a['customFieldValues'] if 'photo' in c['name'])
				if len(value) > 0:
					logging.info(f"{rPayload['type']}: {a['activityFormName']} {a['activityFormId']} {value}")
		rPayload['count'] = count
		rPayload['offset'] = rPayload['offset'] + count
