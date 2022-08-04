import argparse
import csv
import requests
import json
import logging

"""Standalone Python3 app to list activities for a client."""

def listActivityTypes(token):
	"""Return a list of valid activity types

	Parameters:
		token       Engage Integration API token

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.
	"""
	endPoint = 'https://api.salsalabs.org/api/developer/ext/v1/activities/types'
	headers = {
		'authToken': token,
		'content-type': 'application/json'
	}
	r = requests.get(endPoint, headers=headers)
	if (r.status_code != 200):
		logging.fatal(f"error: HTTP status code {r.status_code}")
		logging.fatal(json.dumps(json.loads(r.text), indent=4))
		exit(1)
	response = r.json()
	if "errors" in response:
		logging.fatal("Read errors:")
		logging.fatal(json.dumps(response['errors'], indent=4))
	dPayload = r.json()['payload']
	dResults = dPayload['results']
	types = (r['code'] for r in dResults)
	return types

def listActivities(token, writer):
	"""Read a list of activity. Write typically useful information
		to a CSV file.

	Parameters:
		token       Engage Integration API token
		writer		CSV writer to receive output

	Errors:
		HTTP errors are also noisily fatal.
		Engage-specific errors are also noisily fatal.
	"""

	# Engage API endpoint
	searchURL = 'https://api.salsalabs.org/api/developer/ext/v1/activities'
	

	# HTTP headers to send the API token.
	headers = {
		'authToken': token,
		'content-type': 'application/json'
	}

	count = 20
	offset = 0
	sortField = "name"
	sortOrder="ASCENDING"
	activityTypes = listActivityTypes(token)
	if activityTypes == None:
		logging.fatal("Error: could not retrieve activity type list")
		exit(1)
	formType = ','.join(activityTypes)
	columns = "type,dateCreated,datePublished,status,visibility,type,name".split(",")
	writer.writerow(columns)
	while count > 0:
		queries = f"?types={formType}&sortField={sortField}&sortOrder={sortOrder}&count={count}&offset={offset}"
		u = searchURL + queries
		# logging.info(f"URL: {u}")
		r = requests.get(u, headers=headers)
		if (r.status_code != 200):
			logging.fatal(f"error: HTTP status code {r.status_code}")
			logging.fatal(json.dumps(json.loads(r.text), indent=4))
			exit(1)
		response = r.json()
		if "errors" in response:
			logging.fatal("Read errors:")
			logging.fatal(json.dumps(response['errors'], indent=4))
		dPayload = r.json()['payload']
		count = dPayload['count']
		if count == 0:
			continue
		dResults = dPayload['results']
		for r in dResults:
			status = r['status']
			if status == "PUBLISHED":
				published = r['publishDate'][0:10]
			else:
				published = ""
			row = [r['id'],
				r['createDate'][0:10],
				published,
				status,
				r['visibility'],
				r['type'],
				r['name']]
			writer.writerow(row)
			offset = offset + count

def main():
	"""Program entry point. Uses a user-provided id, retrieves
	activities and outputs JSON to the console."""

	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
	parser = argparse.ArgumentParser(
		description='See list of forms for an form type')
	parser.add_argument('--token', action='store', required=True,
						help='Engage Integration API token')

	args = parser.parse_args()
	with open("activity_list.csv", "w") as f:
		w = csv.writer(f)
		listActivities(args.token, w)
		f.flush()
		f.close()


if (__name__) == "__main__":
	main()
