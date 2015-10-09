import os
import sys
import StringIO
import requests
import logging
import twitter
from BeautifulSoup import BeautifulSoup as BS
import datetime

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARN)

TODAY = datetime.date.today()
TODAYPLUS10 = TODAY + datetime.timedelta(days=10)
TODAYMINUS7 = TODAY - datetime.timedelta(days=7)
USERAGENT = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}

def login(site):
	if site=="ridgefield":
		siteid=5
	elif site=="wilton":
		siteid=7
	else:
		raise Exception("invalid site")
	secrets = open("../autotweet/.secret-%s" % site).read().strip().split(";")
	_, username, password, _, _, _, _ = secrets	
	#r = requests.get("http://www.joyridestudio.com/admin/", headers=USERAGENT, allow_redirects=True)
	#cookies = r.cookies
	#formdata = {'action': 'Sec.doLogin', 'username': username, 'password':password}
	#r = requests.post("http://www.joyridestudio.com/admin/index.cfm?action=", headers=USERAGENT, data=formdata, cookies=cookies, allow_redirects=False)
	r = requests.get("http://www.joyridestudio.com/admin/", allow_redirects=True)
	cookies = r.cookies
	formdata = {'action': 'Sec.doLogin', 'username': username, 'password':password}
	r = requests.post("http://www.joyridestudio.com/admin/index.cfm?action=", data=formdata, cookies=cookies, allow_redirects=False)
	# set site cookie
	r = requests.get(r"http://www.joyridestudio.com/admin/index.cfm?action=Register.setSite&siteid=%s" % siteid, cookies=cookies, allow_redirects=False)
	return cookies
	
def getCustomers(cookies):
	log.info("fetching customers")
	r = requests.get("http://www.joyridestudio.com/admin/index.cfm?action=Report.exportEmails", headers=USERAGENT, cookies=cookies)
	return r.text.encode("utf-8")
	
def saveCustomers(cookies, site):
	log.info("saving customers")
	with open("customers-%s.csv" % site, "wb") as fp:
		fp.write(getCustomers(cookies))
		
def getSales(cookies):
	r = requests.get("http://www.joyridestudio.com/admin/index.cfm?action=Report.allSalesByDate", headers=USERAGENT, cookies=cookies)
	log.info("fetching sales from %s to %s" % (TODAYMINUS7, TODAY))
	url = "http://www.joyridestudio.com/admin/index.cfm?action=Report.allSalesByDate&start=%s/%s/%s&end=%s/%s/%s&go=GO" % \
			(TODAYMINUS7.month, TODAYMINUS7.day, TODAYMINUS7.year-2000, TODAY.month, TODAY.day, TODAY.year-2000)
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	formdata = {'export': 'csv', 'time':'0'}
	r = requests.post("http://www.joyridestudio.com/admin/index.cfm?action=Report.allSalesByDate", headers=USERAGENT, cookies=cookies, data=formdata)
	return r.text.encode("utf-8")	
	
def saveSales(cookies, site):
	log.info("saving sales")
	with open("sales-%s.csv" % site, "wb") as fp:
		fp.write(getSales(cookies))

def getAttendance(cookies):
	#print requests.utils.dict_from_cookiejar(cookies)	
	r = requests.get("http://www.joyridestudio.com/admin/index.cfm?action=Report.attendanceExport", headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	log.info("fetching attendance from %s to %s" % (TODAYMINUS7, TODAYPLUS10))
	url = "http://www.joyridestudio.com/admin/index.cfm?action=Report.attendanceExport&roomid=1&start=%s/%s/%s&end=%s/%s/%s&go=GO" %  \
		(TODAYMINUS7.month, TODAYMINUS7.day, TODAYMINUS7.year-2000, TODAYPLUS10.month, TODAYPLUS10.day, TODAYPLUS10.year-2000)
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	url="http://www.joyridestudio.com/admin/index.cfm?action=Report.attendanceExport&roomid=1&export=csv"
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	return r.text.encode("utf-8")	
		
def saveAttendance(cookies, site):
	log.info("saving attendance")
	with open("attendance-%s.csv" % site, "wb") as fp:
		fp.write(getAttendance(cookies))

def getSeries(cookies):
	log.info("fetching open series")
	r = requests.get("http://www.joyridestudio.com/admin/index.cfm?action=Report.exportAllOpenSeries", headers=USERAGENT, cookies=cookies)
	return r.text.encode("utf-8")
	
def saveSeries(cookies, site):
	log.info("saving open series")
	with open("openseries-%s.csv" % site, "wb") as fp:
		fp.write(getSeries(cookies))
	
def main(site):
	cookies = login(site)
	saveCustomers(cookies, site)
	saveSales(cookies, site)
	saveAttendance(cookies, site)
	saveSeries(cookies, site)
	log.info("done")
	
if __name__ == "__main__":
	main()
