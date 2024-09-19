import requests
import urllib3
from bs4 import BeautifulSoup
import logging
from http.client import HTTPConnection


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


url = "https://perfcomp.ipa.dataart.net/admin/delete"

payload='id=1978'
headers = {
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Content-Length': '7',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'DNT': '1',
  'Host': 'perfcomp.ipa.dataart.net',
  'Origin': 'https://perfcomp.ipa.dataart.net',
  'Referer': 'https://perfcomp.ipa.dataart.net/admin/users',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'Cookie': 'PHPSESSID=89gm68hd1i3c9kvvqv32e7mhir'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False,)

print(response.text)
