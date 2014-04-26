import sys
import requests
import logging
import getpass
password = getpass.getpass("password:")
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

#user_agent = {'User-agent': 'Mozilla/5.0'}
s = requests.Session() 
#r = s.get("http://joyrideridgefield.com/admin/")
#print r.text
payload = {'action': 'Sec.doLogin', 'username': 'webrobot', 'password':password}
#r = s.post("http://www.joyrideridgefield.com/admin/index.cfm?action=", data=payload, allow_redirects=True)
cookies = #
r = s.get("http://www.joyrideridgefield.com/admin/index.cfm?action=Booker.home", cookies=cookies)

print "-" * 40
print r.status_code
for item in s.cookies:
    print item 
print r.text
