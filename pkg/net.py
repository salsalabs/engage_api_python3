import json
import requests
import time
import urllib

from urllib.parse import urlunsplit

class Endpoint:
	def __init__(self, **kwargs):
		""" Class to represent the key information for reading from an Engage API enpoint.
		    The class provides access to the keyword arguments (below).  The class also
			provides access to these two derived values:

			-- url: The full endpoint URL
			-- session: an instance of requests.Session that contains the provided token.

		Keyword arguments:
		endpoint -- API endpoint.  For example, "/api/integration/ext/v1/activities/search"
		host     -- Engage hostname, defaults to "api.salsalabs.org"
		method   -- HTTP method.  For example  "POST" or  "GET"
		token    -- API token

		:raises:
		NameError: missing parameters
		ValueError: invalid JSON in the request

		:example:
		from pkg.net import Endpoint
		ep = Endpoint(endpoint="/api/integration/ext/v1/activities/search",
					 method="POST",
					 token=token)
		or

		from pkg.net import Endpoint
		parms = {
			"endpoint": "/api/integration/ext/v1/activities/search",
			"method": "POST",
			"token": token
		}
		ep = Engage(**parms)
		"""

		self.endpoint = None
		self.host = None
		self.method = None
		self.token = None

		self.__dict__.update(**kwargs)
		if self.endpoint == None:
			raise NameError('endpoint')
		if self.host == None:
			self.host = 'api.salsalabs.org'
		if self.method == None:
			raise NameError('method')
		if self.token == None:
			raise NameError('token')
		self.session = requests.Session()
		self.session.headers = {
			'Content-Type': 'application/json',
			'authToken': self.token
		}
		parts = ('https', self.host, self.endpoint, None, None)
		self.url = urlunsplit(parts)

class Invoker:
	def __init__(self, endpoint):
		""" Class to send a request payload to an Engage API endpoint and return the response payload.

			-- url: The full endpoint URL
			-- session: an instance of requests.Session that contains the provided token.

		Arguments:
		endpoint -- API endpoint object

		:returns:
		Returns the response payload

		:raises:
		NameError: missing parameters
		ValueError: invalid JSON in the request

		:example:
		from pkg.net import Endpoint, Invoker
		e = Endpoint(endpoint="/api/integration/ext/v1/activities/search",
					 method="POST",
					 token=token)
		i = Invoker(endpoint)
		request = { ... }
		response = i.invoke(request)
		"""

		self.endpoint = endpoint
		if self.endpoint == None:
			raise NameError('endpoint')

	def invoke(self, request):
		""" Execute the request and return the response.  You can expect
			the response to be JSON.

		Arguments:
		request -- request payload to submit

		:return:
		response -- response payload from the call

		:raises:
			URLError  -- invalid URL
			HTTPError -- The usual HTTP errors (4xx, 5xx, etc)
			NameError -- Raised if method is not valid
		"""

		complete = False
		response = None

		while not complete:
			if self.endpoint.method == 'POST':
				response = self.endpoint.session.post(url=self.endpoint.url, json=request)
			elif self.endpoint.method == 'GET':
				response = self.endpoint.session.get(url=self.endpoint.url, params=request)
			elif self.endpoint.method == 'PUT':
				response = self.endpoint.session.put(url=self.endpoint.url, json=request)
			elif self.endpoint.method == 'DEL':
				response = self.endpoint.session.delete(url=self.endpoint.url, params=request)
			else:
				raise NameError(f"Method {self.method}")

			needNap = False
			if response.status_code != 200:
				if response.status_code == 429:
					if "Requested batch size exceeds the allowed size" in response.text:
						raise Exception(f"Invoker: HTTP status 429, {response.text}")
					else:
						print(f"Invoker: HTTP status 429, {response.text}")
						needNap = True
				else:
					raise Exception(f"HTTP Status {response.status_code}, {self.endpoint.url}")
			else:
				if "Your per minute call rate" in response.text:
					print("Invoker: Warning: {response.text}")
					needNap = True
				else:
					complete = True
			if needNap:
				print("Invoker: napping...")
				time.sleep(30)

		return response.json()['payload']
