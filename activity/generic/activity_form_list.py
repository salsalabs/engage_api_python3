import argparse
import csv
import requests
import json
import logging

from pkg.net import EngageNet

"""Python3 app to list all activities for a client and export the 
   results as a CSV. Each line of the CSV is an action and contains
   the usual information that clients want to see."""

def listActivityTypes(webToken):
	"""Return a list of valid activity types

	Parameters:
		webToken  	Engage Web Developer API token

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.
	"""

	# Parameters for EngageNet
	params = {
	    'endpoint': 'api/developer/ext/v1/activities/types',
	    'host': 'api.salsalabs.org',
	    'token': webToken,
	    'method': 'GET',
	    'request': ""
	}
	net = EngageNet(**params)
	r = net.run()
	p = r['payload']
	r = p['results']
	t = list((s['code'] for s in r))
	return t

def listActivities(intToken, webToken, writer):
	"""Read a list of activity. Write typically useful information
		to a CSV file.

	Parameters:
		intToken    Engage Integration API token
		webToken	Engage Web Developer API token
		writer		CSV writer to receive output

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.
	"""

	activityTypes = listActivityTypes(webToken)
	if activityTypes == None:
		logging.fatal('Error: could not retrieve activity type list')
		exit(1)

	columns ='id,dateCreated,datePublished,status,visibility,type,name'.split(',')
	writer.writerow(columns)

	count = 20
	offset = 0
	while count > 0:
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
			row = [r['id'],
				r['createDate'][0:10],
				published,
				r['status'],
				r['visibility'],
				r['type'],
				r['name']]
			(print row)
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

	args = parser.parse_args()
	with open('activity_list.csv', 'w') as f:
		w = csv.writer(f)
		listActivities(args.intToken, args.webToken, w)
		f.flush()
		f.close()


if (__name__) == '__main__':
	main()
