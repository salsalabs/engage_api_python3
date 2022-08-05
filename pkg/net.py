import json
import requests
import time
import urllib

from urllib.parse import urlunsplit

class EngageNet:
	def __init__(self, **kwargs):
		""" Initializes the instance. Raises errors for invalid inputs.

		Keyword arguments:
		endpoint -- API endpoint.  For example, "/api/integration/ext/v1/activities/search"
		host     -- Engage hostname, defaults to "api.salsalabs.org"
		method   -- HTTP method.  For example  "POST" or  "GET"
		request  -- JSON request
		token    -- API token

		:raises:
		NameError: missing parameters
		ValueError: invalid JSON in the request

		:example:
		from pkg.net import EngageNet
		net = Engage(endpoint="/api/integration/ext/v1/activities/search",
					 method="POST",
					 request=rqt,
					 token=token)
		or

		from pkg.net import EngageNet
		request = {
			"endpoint": "/api/integration/ext/v1/activities/search",
			"method": "POST",
			"request": rqt,
			"token": token
		}
		net = Engage(**request)
		"""

		self.endpoint = None
		self.host = None
		self.method = None
		self.request = None
		self.token = None

		self.__dict__.update(**kwargs)
		if self.endpoint == None:
			raise NameError('endpoint')
		if self.host == None:
			self.host = 'api.salsalabs.org'
		if self.method == None:
			raise NameError('method')
		if self.request == None:
			raise NameError('request')
		if self.token == None:
			raise NameError('token')
		self.session = requests.Session()
		self.session.headers = {
			'Content-Type': 'application/json',
			'authToken': self.token
		}

	def run(self):
		""" Execute the request and return the response.  You
		can expect the response to be JSON.

		:return:
		requests.Response object

		:raises:
			URLError:
			HTTPError:
		"""

		parts = ('https', self.host, self.endpoint, None, None)
		url = urlunsplit(parts)
		complete = False
		response = None

		while not complete:
			if self.method == 'POST':
				response = requests.post(url=url, json=self.request, headers=self.session.headers)
			else:
				response = self.session.get(url, params=self.request)

			needNap = False
			if response.status_code != 200:
				if response.status_code == 429:
					print("EngageNet: HTTP status 429, waiting for a bit")
					print("EngageNet: ", response.text)
					needNap = True
				else:
					raise Exception("HTTP Status " + str(response.status_code), url)
			else:
				if "Your per minute call rate" in response.text:
					print("EngageNet: found raw call rate message")
					needNap = True
				else:
					complete = True
			if needNap:
				print("EngageNet: napping...")
				time.sleep(30)

		s = response.text
		return json.loads(s)
