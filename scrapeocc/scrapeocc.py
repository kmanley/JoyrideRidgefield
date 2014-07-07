# Quick and dirty hack to check occupancy for a site where we don't have admin
import sys
import sqlite3
import StringIO
import requests
import logging
import twitter
from BeautifulSoup import BeautifulSoup as BS
import datetime
secrets = open(".secret").read().strip().split(";")
baseurl, username, password = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)

conn = sqlite3.connect("occupancy.db")
SITENAMES = ["westport", "darien"]
SITES = {"westport":"http://www.%s/reserve/index.cfm?action=Reserve.chooseClass&site=1&n=Westport" % baseurl,
	 "darien":"http://www.%s/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien" % baseurl}
CAPACITY = {"westport":44, "darien":40}
TODAY = datetime.datetime.today()

# TODO: sold out classes (classfull class) have a link that does not contain date/time info, just a "sorry, class full msg"
# so we need to extract date/time/instructor here instead of in getOccupancy
def getBookableLinks(site, cookies):
	r = requests.get(SITES[site], headers=userAgent, cookies=cookies)
	soup = BS(r.text)
	blocks = soup.findAll("div", attrs={"class":["scheduleBlock", "scheduleBlock classfull"]})
	for block in blocks:
	    #print block
	    link = block.find("a")
	    if link:
		if link.span.text and link.span.text.lower().find("cycle")>-1:
  		    #print link.span.text, link.get("href")
                    day = int(link.parent.parent["class"][3:])
                    sdate = soup.findAll("span", attrs={"class":"thead-date"})[day].text
                    dateparts = sdate.split(".")
                    month = int(dateparts[0])
                    day = int(dateparts[1])
       		    instr = block.find("span", attrs={"class":"scheduleInstruc active"}).text
		    stime = block.find("span", attrs={"class":"scheduleTime active"}).text
                    # 11:00 AM60min
                    hour = int(stime.split(":")[0])
                    minute = int(stime.split(" ")[0].split(":")[-1])
                    if stime.split(" ")[1].startswith("PM") and hour < 12:
                        hour += 12
                    if block["class"].find("classfull") > -1:
                        soldout = True
                    else:
                        soldout = False
                    year = (TODAY + datetime.timedelta(days=day)).year
                    dt = datetime.datetime(year, month, day, hour, minute, 0)
                    yield dt, instr, soldout, link.get("href")
	    else:
		pass #print "no link"

def getOccupancy(url, cookies):
    r = requests.get("http://www.%s%s" % (baseurl, url), headers=userAgent, cookies=cookies)
    soup = BS(r.text)
    details = soup.find("div", attrs={"class":"yui-u", "id":"sidebar"})
    if not details:
        print "found sold out class %s" % url
        return datetime.datetime(1900,1,1,0,0,0), "Unknown", 0, 0, 100
    ps = details.findAll("p")
    date = ps[0].text.strip()[len("Date:")+5:]
    dateparts = date.split("/")
    month = int(dateparts[0])
    day = int(dateparts[1])
    year = 2000 + int(dateparts[2])
    time = ps[1].text.strip()[len("Time:"):]
    timeparts = time[:-1].split(":")
    hour = int(timeparts[0])
    minute = int(timeparts[1])
    if time[-1].lower() == "p" and hour < 12:
        hour += 12
    dt = datetime.datetime(year, month, day, hour, minute, 0)
    instr = ps[2].text.strip()[len("Instructor:"):]
    block = soup.find("div", attrs={"id":"spotwrapper"})
    avail = 0
    unavail = 0
    for item in block:
        if not hasattr(item, "name"):
            continue
        if item.name == "span":
            unavail += 1
        elif item.name == "a":
            avail += 1
    total = avail + unavail
    occ = float(unavail) / total * 100.
    return dt, instr, unavail, total, occ

userAgent = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}
NDAYS = 1 
target_date = datetime.date.today() + datetime.timedelta(days=NDAYS)
starget_date = target_date.strftime("%a %b") + " " + str(target_date.day)

r = requests.get("http://www.%s/reserve/index.cfm?action=Account.login" % baseurl, headers=userAgent, allow_redirects=True)
cookies = r.cookies
formdata = {'action': 'Account.doLogin', 'username': username, 'password':password}
r = requests.post("https://www.%s/reserve/index.cfm?action=" % baseurl, data=formdata, headers=userAgent, cookies=cookies, allow_redirects=False)

# this gets calendar page; need to find td class="... today" to get classids of today's classes
# 	<div class="scheduleBlock">
#	<a href="/reserve/index.cfm?action=Reserve.chooseSpot&amp;classid=16601">
#r = requests.get("http://www.%s/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien" % baseurl, cookies=cookies)

curs = conn.cursor()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
for sitename in SITENAMES:
    print sitename
    for item in getBookableLinks(sitename, cookies):
        dt, instr, soldout, url = item
        if dt.date() > tomorrow:
            break   
        if soldout:
            unavail = total = CAPACITY[sitename]
        else:
            dt, instr, unavail, total, occ = getOccupancy(url, cookies)
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
        curs.execute("insert or replace into occ values (?, ?, ?, ?)", (dt, instr, unavail, total))
        conn.commit()

    print "-" * 40



