#!/usr/bin/python 
# coding=utf-8

import httplib;
from HTMLParser import HTMLParser
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--dico", dest="dico", help="choose the dictionnary to use (ex: enfr, fren)", metavar="DICO")
(options, args) = parser.parse_args()

if len(args) != 1:
  parser.error("incorrect number of arguments")

word = args[0]

if not options.dico:
  dico = "enfr"
else:
  dico = options.dico

class FailedException(Exception):
	def __init__(self, failed_request, status, reason, data):
		self.failed_request = failed_request
		self.status = status
		self.reason = reason
		self.data = data


class WordReferenceHTMLParser(HTMLParser):
  translation = dict()
  
  def handle_starttag(self, tag, attrs):
    attrs_dict = dict(attrs)
    
    if tag == "td" \
      and attrs_dict.has_key('class') \
      and (attrs_dict['class'] == 'FrCN2'):
        pass

    elif self.waitForSpan and tag == "span":
      pass

  def handle_data(self, data):
    pass

  def handle_endtag(self, tag):
    pass

class CookieStore:
	cookies = dict()

	def add_cookies(self, cookies_str):
		if cookies_str:
			for c in re.split(', ', cookies_str):
				cookie = re.split('=', re.split('; ', c, 1)[0], 1)
				self.cookies[cookie[0]] = cookie[1]

	def cookies_as_string(self):
		cookies_str = ''
		first = True
		for (k, v) in self.cookies.items():
			if not first:
				cookies_str += '; '
			else:
				first = False
		 
			cookies_str += '='.join([k, v])
		return cookies_str
	def has_cookie(self):
		return len(self.cookies) > 0


class ChainedHttpRequest:
	def __init__(self, method, url, expectedCode, next_request = None, headers = {}, body = ''):
		self.method = method
		self.url = url
		self.expectedCode = expectedCode
		self.headers = headers
		self.body = body
		self.next_request = next_request
	
	def process(self, connection, cookie_store, referer = None):
		headers = self.headers.copy()
		
		if referer:
			headers['Referer'] = referer
		
		if cookie_store.has_cookie():
			headers['Cookie'] = cookie_store.cookies_as_string()
		
		connection.request(self.method, self.url, self.body, headers)
		response = connection.getresponse()
		
		if response.status == self.expectedCode:
			cookie_store.add_cookies(response.getheader('Set-Cookie'))
			
			if self.next_request:
				response.read()
				return self.next_request.process(connection, cookie_store, self.url)
			else:
				return response.read()
		else:
			raise FailedException(self, response.status, response.reason, response.read())


request = ChainedHttpRequest('GET', '/' + dico + '/' + word, httplib.OK)
request = ChainedHttpRequest('GET', '/', httplib.OK, request)

store = CookieStore()

connection = httplib.HTTPConnection('www.wordreference.com')
connection.set_debuglevel(9)

res = request.process(connection, store, 'http://www.wordreference.com/')

parser = WordReferenceHTMLParser()
parser.feed(res)


