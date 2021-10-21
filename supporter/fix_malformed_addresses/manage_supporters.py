import argparse
import csv
import json
import logging
import queue
import requests
import threading

def get_metrics(args):
	"""
	Read the current Engage metrics object. The metrics object
	contains both statistical information and information about
	how many actions are left in the current timeslot and the
	maximum number of records that can be retrieved.

	This function reads the Engage response, converts it from
	JSON, then returns the "payload" item of the response.

	Summary
	-------
	get_metrics(args: object) -> :object

	Parameters
	----------
	args : object
		Command-line arguments containing the Integration API Token

	Errors
	------
	* HTTP and requests errors
	* HTTP Status code not 200

	Errors are noisy and fatal.

	See
	---
	https://api.salsalabs.org/help/integration#operation/getCallMetrics

    """
	headers = {"authToken": args.token,
	           "Content-Type": "application/json"}
	url = "https://api.salsalabs.org/api/integration/ext/v1/metrics"
	r = requests.get(url, headers=headers)
	print(r)
	if (r.status_code != 200):
		logging.error("HTTP status code: " + str(r.status_code) + " : " + url)
		logging.fatal(r.text)
		if r.status_code == 429:
			time.sleep(10)
		else:
			exit(1)
	return r.json()["payload"]

def get_delete_payload(thread_id, args, ids):
	"""
	Deletes supporters whose supporterId matches one of the ids
	in `ids`. Returns the payload from Engage.

	Summary
	-------
	get_delete_payload(args: object, id: array<string>) -> :object

	Parameters
	----------
	args : object
		Command-line arguments containing the Integration API Token

	ids : array<string>
		List of supporterIds to delete for

	Errors
	------
	* HTTP and requests errors
	* HTTP Status code not 200

	Errors are noisy and fatal.

	See
	---
	https://api.salsalabs.org/help/integration#operation/deleteSupporters

    """
	headers = {"authToken": args.token,
	           "Content-Type": "application/json"}

	# The list of supporter IDs needs to be embedded in the request payload
	# as a list of supporter records.

	supporters = [ {"supporterId": id} for id in ids ]
	payload = {"payload": {"supporters": supporters}}

	url = "https://api.salsalabs.org/api/integration/ext/v1/supporters"

	success = false
	while not(success):
		r = requests.delete(url, headers=headers, data=unicode(json.dumps(payload)))
		if (r.status_code == 200):
			success = true
			logging.error(f"Thread {thread_id}: HTTP status code: {r.status_code} :  url")
			logging.error(json.dumps(r.json(), indent=4))
			if r.status_code == 429:
				logging.error(f"Thread {thread_id}: napping...")
				time.sleep(10)
				success = false
			else:
				exit(1)
	return r.json()["payload"]

def get_search_payload(args, ids):
	"""
	Searches for supporters whose supporterId matches one
	of the ids in `ids`. Returns the payload from Engage

	Summary
	-------
	get_search_payload(args: object, id: array<string>) -> :object

	Parameters
	----------
	args : object
		Command-line arguments containing the Integration API Token

	ids : array<string>
		List of supporterIds to search for

	Errors
	------
	* HTTP and requests errors
	* HTTP Status code not 200

	Errors are noisy and fatal.

	See
	---
	https://api.salsalabs.org/help/integration#operation/supporterSearch

    """
	headers = {"authToken": args.token,
	           "Content-Type": "application/json"}
	payload = {"payload":
				{"identifiers": ids,
				"identifierType": "SUPPORTER_ID"}}
	url = "https://api.salsalabs.org/api/integration/ext/v1/supporters/search"

	r = requests.post(url, headers=headers, data=json.dumps(payload))
	if (r.status_code != 200):
		logging.fatal("HTTP status code: " + str(r.status_code)  + " : " + url)
		# logging.fatal(json.dumps(r.json(), indent=4))
		exit(1)
	return r.json()["payload"]

def process(i, args, payload_getter, q, w):
	"""
	This function does the heavy lifting. It sends each batch to the
	payload_getter. That returns a response payload. The payload is
	parsed for supporters. Supporters are written to the provide csv.Writer.

	Parameters
	----------
		i : int
			Thread ID

		args : object
			Command line arguments, used primarily for the Engage
			Integration API token

		payload_getter: function
			A function to do something on Engage and return a payload
			 of supporters

		q : q.Queue
			Queue of batches.  

		w : csv.Writer
			Used to write the supporters to a CSV file

	"""
	total = 1
	while not(q.empty()):
		batch = q.get()
		if (total % 10 == 0):
			logging.info(f"Process-{i}: popped batch {total}")
		total += 1
		payload = payload_getter(args, batch)
		rows = [ [ r["supporterId"], r["result"]] for r in payload["supporters"]]
		w.writerows(rows)
		if args.verbose:
			[ logging.info("\n".join(row)) for row in rows ]
	print(f"process-{i}: done")

def main():
	"""
	Program entry point. Accepts and validates the command-line arguments.
	The ID file is broken into "maxBatchSize" chunks. Each chunk is used
	to

	* get info about the supporters in that chunk, or
	* delete the supporters in the chunk.

	The results of getting/deleteing supproters are written to the CSV file
	provided in the calling arguments.

	Note
	----
	This app is written to work in both Python 2.7.x and Python 3.x.x.
	It will most likely be used on systems with the older release of
	Python.

	Summary
	-------
	$ python manage_supporters.py --help

	usage: manage_supporters.py [-h] --token TOKEN --id_file ID_FILE --csv_file
                            CSV_FILE
                            {check,delete}

Accept a file of supporterIDs. Look them up in Engage. Write IDs and status to
a CSV.

positional arguments:
  {check,delete}    Available commands

optional arguments:
  -h, --help           show this help message and exit
  --token TOKEN        Engage Integration API token
  --id_file ID_FILE    CSV file of supporterIDs
  --csv_file CSV_FILE  Output. Shows supporterID and found/not found

	Arguments
	---------
	command
		A list of functions that this app can perform.
		* check: save the supporterId and status for every supporterId in ID_FILE
		* delete: delete the supproters for very supporterId in ID_FILE

	TOKEN
		The mult-character Engage Integration API token for the client

	ID_FILE
		A CSV file of supporterIds to check or delete. The first column should
		contain Engage supporterIds (CRM Constituent UUIDs).  All other contents
		are ignored.

	CSV_FILE
		The file where this app should write results. Each row contains
		two fields.

		- SupporterID: Engage supporterID
		- Result: One of FOUND, NOT_FOUND, DELETED

	Errors
	------
	* HTTP and requests errors
	* HTTP Status code not 200

	Errors are noisy and fatal.

    """

	parser = argparse.ArgumentParser(description="Accept a file of supporterIDs. Look them up, or delete them, in Engage. Write IDs and status to a CSV.")
	parser.add_argument("command", choices=['check', 'delete'], default="check", help="Available commands")
	parser.add_argument("--token", required=True, help="Engage Integration API token")
	parser.add_argument("--id_file", required=True, help="CSV of supporterIDs")
	parser.add_argument("--csv_file", required=True, help="Output. Shows supporterID and found/not found")
	parser.add_argument("--verbose", action="store_true", help="See the results on the console, too.")
	args = parser.parse_args()
	logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
	metrics = get_metrics(args)
	maxBatchSize = metrics["maxBatchSize"]
	q = queue.Queue()

	with open(args.id_file, "r") as f:
		r = csv.reader(f)
		ids = [ row[0] for row in r if len(row[0]) == 36]
		f.close()

		batches = [ ids[offset:offset+maxBatchSize] for offset in range(0, len(ids), maxBatchSize)]
		logging.info(args.id_file + " contains " + str(len(ids)) + " records in " + str(len(batches)) + " batches.")
		[ q.put(b) for b in batches ]
		payload_getter = get_search_payload
		if args.command == "delete":
			payload_getter = get_delete_payload
		with open(args.csv_file, "w") as f:
			w = csv.writer(f)
			w.writerow(["SupporterID", "Result"])
			for i in range(1, 6):
				t = threading.Thread(target=process, args=(i, args, payload_getter, q, w))
				t.start()
			q.join()
			f.close()

if __name__ == "__main__":
	main()
