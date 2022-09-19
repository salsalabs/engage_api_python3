from pkg.net import Endpoint, Invoker
import argparse
import json

def main():
	"""Application to display current Engage API Metrics.  You provide a token.  If you
	   are using an Engage UAT host, then you provide the hoostname as well."""
	parser = argparse.ArgumentParser( description='Display the current Engage API metrics')
	parser.add_argument('--token', action='store', required=True,
						help='Engage Integration API token')
	parser.add_argument('--host', action="store", required=True,
						help="API hostname, only useful for Engage support staff...")
	args = parser.parse_args()
		

	if args.host == None:
		args.host = "api.salsalabs.org"	
	parms = {
		"endpoint": '/api/integration/ext/v1/metrics',
		"method": 'GET',
		"host": args.host,
		"token": args.token}
	ep = Endpoint(**parms)
	i = Invoker(ep)
	s = i.invoke(None)
	print(json.dumps(s, sort_keys=True, indent=4))

if __name__ == '__main__':
	main()
