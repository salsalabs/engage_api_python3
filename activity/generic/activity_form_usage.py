import argparse
import csv
import requests
import json
import logging

from pkg.net import EngageNet

"""Python3 app to list all activities for a client and export the 
   results as a CSV. Each line of the CSV is an action and contains
   the usual information plus the number of submits for the activity."""

def listActivityTypes(token):
	"""Return a list of valid activity types

	Parameters:
		token  	access token for Engage Web Developer API

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.

	See:
		https://api.salsalabs.org/help/web-dev#operation/getActivityFormTypes

	Returns:
		List of valid activity types

	"""

	# Parameters for EngageNet
	params = {
	    'endpoint': 'api/developer/ext/v1/activities/types',
	    'host': 'api.salsalabs.org',
	    'token': token,
	    'method': 'GET',
	    'request': ""
	}
	net = EngageNet(**params)
	r = net.run()
	p = r['payload']
	r = p['results']
	t = list((s['code'] for s in r))
	return t

def getLastActionDate(token, batchSize, activity):
	"""Search for activities of the given type with the specified ID.
	   Read through the actions taken and record the last date.
	   Return that.

	Parameters:
		token  		access token for Engage Integration API
		batchSize	maximum number of records to read a a time
		activity 	activity record, see "response" in the doc

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.

	See:
		https://api.salsalabs.org/help/integration#operation/activitySearch
		https://api.salsalabs.org/help/web-dev#operation/getActivityFormTypes

	Returns:
		Total 	integer	Number of actions (donations, attendees, etc.)

	"""

	# Parameters for EngageNet

	payload = {
		"payload" : {
			'activityFormIds': [ activity['id'] ],
			# 'type': activity['type'],
			'count': batchSize,
			'offset': 0
		}
	}

	params = {
	    'endpoint': 'api/integration/ext/v1/activities/search',
	    'host': 'api.salsalabs.org',
	    'token': token,
	    'method': 'POST',
	    'request': payload
	}

	lastActionDate = ""

	while payload['payload']['count'] > 0:
		net = EngageNet(**params)
		r = net.run()
		p = r['payload']
		if p['count'] > 0:
			currentMax = max(list((a['activityDate'] for a in p['activities'])))
			lastActionDate = max(lastActionDate, currentMax)
		payload['payload']['offset'] = payload['payload']['offset'] + p['count']
		payload['payload']['count'] = p['count']
	return lastActionDate

def listActivityForms(intToken, webToken, batchSize, defOffset, writer):
	"""Read a list of activity forms. Write typically useful information
		to a CSV file.

	Parameters:
		intToken   	Engage Integration API token
		webToken   	Engage Web Develper API token
		batchSize	number of records per batch, typically 20. Can be more.
		defOffset	start reading at this offset.
		writer		CSV writer to receive output

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.

	See:
		https://api.salsalabs.org/help/web-dev#operation/getActivityFormList

	Returns:
		Nothing
	"""

	activityTypes = listActivityTypes(webToken)
	if activityTypes == None:
		logging.fatal('Error: could not retrieve activity type list')
		exit(1)

	columns ='id,dateCreated,datePublished,status,visibility,type,name,LastActionDate'.split(',')
	writer.writerow(columns)

	count = batchSize
	offset = defOffset
	while count == batchSize:
		queries = {
			'formType': ','.join(activityTypes),
			'sortOrder': 'ASCENDING',
			'count': count,
			'offset': offset
		}
		params = {
		    'endpoint': 'api/developer/ext/v1/activities',
		    'host': 'api.salsalabs.org',
		    'token': webToken,
		    'method': 'GET',
		    'request': queries
		}
		net = EngageNet(**params)
		response = net.run()

		payload = response['payload']
		count = payload['count']
		if count == 0:
			continue
		results = payload['results']
		for r in results:
			if r['status'] == 'PUBLISHED':
				published = r['publishDate'][0:10]
			else:
				published = ""
			lastActionDate = getLastActionDate(intToken, batchSize, r)
			row = [r['id'],
				r['createDate'][0:10],
				published,
				r['status'],
				r['visibility'],
				r['type'],
				r['name'],
				lastActionDate[0:10]]
			print(row)
			writer.writerow(row)
		offset = offset + count

def main():
	"""Program entry point. Uses a user-provided id, retrieves
	activities and outputs JSON to the console."""

	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
	parser = argparse.ArgumentParser(
		description='See list of forms for an form type')
	parser.add_argument("--intToken", action='store', required=True,
						help='Engage Integration API token')
	parser.add_argument('--webToken', action='store', required=True,
						help='Engage Web Developer API token')
	parser.add_argument('--batchSize', action='store', required=False,
						type=int, default=20,
						help="Number of records per batch, typically 20")
	parser.add_argument('--offset', action='store', required=False,
						type=int, default=0,
						help="Start reading at this offset. Helpful for outages.")

	args = parser.parse_args()
	with open('activity_usage.csv', 'w') as f:
		w = csv.writer(f)
		listActivityForms(args.intToken, args.webToken, args.batchSize, args.offset, w)
		f.flush()
		f.close()


if (__name__) == '__main__':
	main()
