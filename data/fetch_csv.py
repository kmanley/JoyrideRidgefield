# Quick and dirty script to auto-tweet 
import os
import sys
import StringIO
import requests
import logging
import twitter
from BeautifulSoup import BeautifulSoup as BS
import datetime
secrets = open("../autotweet/.secret").read().strip().split(";")
_, username, password, _, _, _, _ = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)

TODAY = datetime.date.today()
TODAYPLUS10 = TODAY + datetime.timedelta(days=10)
USERAGENT = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}

def login():
	r = requests.get("http://www.joyrideridgefield.com/admin/", headers=USERAGENT, allow_redirects=True)
	cookies = r.cookies
	formdata = {'action': 'Sec.doLogin', 'username': username, 'password':password}
	r = requests.post("http://www.joyrideridgefield.com/admin/index.cfm?action=", headers=USERAGENT, data=formdata, cookies=cookies, allow_redirects=False)
	return cookies
	
def getCustomers(cookies):
	r = requests.get("http://www.joyrideridgefield.com//admin/index.cfm?action=Report.exportEmails", headers=USERAGENT, cookies=cookies)
	return r.text.encode("utf-8")
	
def saveCustomers(cookies):
	print "saving customers"
	with open("customers.csv", "wb") as fp:
		fp.write(getCustomers(cookies))
		
def getSales(cookies):
	r = requests.get("http://www.joyrideridgefield.com/admin/index.cfm?action=Report.allSalesByDate", headers=USERAGENT, cookies=cookies)
	url = "http://www.joyrideridgefield.com/admin/index.cfm?action=Report.allSalesByDate&start=1/21/14&end=%s/%s/%s&go=GO" % (TODAY.month, TODAY.day, TODAY.year-2000)
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	formdata = {'export': 'csv', 'time':'0'}
	r = requests.post("http://www.joyrideridgefield.com/admin/index.cfm?action=Report.allSalesByDate", headers=USERAGENT, cookies=cookies, data=formdata)
	return r.text.encode("utf-8")	
	
def saveSales(cookies):
	print "saving sales"
	with open("sales.csv", "wb") as fp:
		fp.write(getSales(cookies))

def getAttendance(cookies):
	#print requests.utils.dict_from_cookiejar(cookies)	
	r = requests.get("http://www.joyrideridgefield.com/admin/index.cfm?action=Report.attendanceExport", headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	url = "http://www.joyrideridgefield.com/admin/index.cfm?action=Report.attendanceExport&roomid=1&start=1/21/14&end=%s/%s/%s&go=GO" % (TODAYPLUS10.month, TODAYPLUS10.day, TODAYPLUS10.year-2000)
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	url="http://www.joyrideridgefield.com/admin/index.cfm?action=Report.attendanceExport&roomid=1&export=csv"
	r = requests.get(url, headers=USERAGENT, cookies=cookies)
	#print requests.utils.dict_from_cookiejar(r.cookies)	
	return r.text.encode("utf-8")	
		
def saveAttendance(cookies):
	print "saving attendance"
	with open("attendance.csv", "wb") as fp:
		fp.write(getAttendance(cookies))

def getSeries(cookies):
	r = requests.get("http://www.joyrideridgefield.com/admin/index.cfm?action=Report.exportAllOpenSeries", headers=USERAGENT, cookies=cookies)
	return r.text.encode("utf-8")
	
def saveSeries(cookies):
	print "saving open series"
	with open("openseries.csv", "wb") as fp:
		fp.write(getSeries(cookies))
	
def main():
	cookies = login()
	saveCustomers(cookies)
	saveSales(cookies)
	saveAttendance(cookies)
	saveSeries(cookies)
	print "done"
	
if __name__ == "__main__":
	main()
