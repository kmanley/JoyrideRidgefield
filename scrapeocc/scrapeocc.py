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
username, password = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)

conn = sqlite3.connect("occupancy.db")

SITENAMES = ["westport", "darien", "ridgefield"] # TODO: texas

BASEURL = {"westport" : "http://www.joyridestudio.com",
           "darien" : "http://www.joyridestudio.com",
           "ridgefield" : "http://www.joyrideridgefield.com"}

USERAGENT = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}

LOGINGET = {"westport" : "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "darien"   : "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "ridgefield" : "http://www.joyrideridgefield.com/reserve/index.cfm?action=Account.login",}

LOGINPOST = {"westport" : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "darien"   : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "ridgefield" : "http://www.joyrideridgefield.com/reserve/index.cfm?action=",}

CALENDARGET = {"westport":  "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&n=Westport",
	       "darien":    "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien",
               "ridgefield":"http://www.joyrideridgefield.com/reserve/index.cfm?action=Reserve.chooseClass"} # TODO:

CAPACITY = {"westport":44, 
	    "darien":40, 
            "ridgefield":35} # TODO: 35 or 36?

TODAY = datetime.datetime.today()
TOMORROW = TODAY + datetime.timedelta(days=1)

# TODO: sold out classes (classfull class) have a link that does not contain date/time info, just a "sorry, class full msg"
# so we need to extract date/time/instructor here instead of in getOccupancy
def getBookableLinks(site, cookies):
	r = requests.get(CALENDARGET[site], headers=USERAGENT, cookies=cookies)
	soup = BS(r.text)
	blocks = soup.findAll("div", attrs={"class":["scheduleBlock", "scheduleBlock classfull"]})
	for block in blocks:
	    #print block
	    link = block.find("a")
	    if link:
                classtype = link.span.text.lower()
		if ("cycle" in classtype) or ("tabata" in classtype) or ("ride" in classtype) or (site=="ridgefield"):
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
		pass #not bookable - class is in past or cancelled

def getOccupancy(site, url, cookies):
    #print "%s%s" % (BASEURL[site], url)
    #print cookies
    r = requests.get("%s%s" % (BASEURL[site], url), headers=USERAGENT, cookies=cookies)
    soup = BS(r.text)
    #print r.text
    #details = soup.find("div", attrs={"class":"yui-u", "id":"sidebar"})
    #if not details:
    #    print "found sold out class %s" % url
        #return datetime.datetime(1900,1,1,0,0,0), "Unknown", 0, 0, 100
    #ps = details.findAll("p")
    #date = ps[0].text.strip()[len("Date:")+5:]
    #dateparts = date.split("/")
    #month = int(dateparts[0])
    #day = int(dateparts[1])
    #year = 2000 + int(dateparts[2])
    #time = ps[1].text.strip()[len("Time:"):]
    #timeparts = time[:-1].split(":")
    #hour = int(timeparts[0])
    #minute = int(timeparts[1])
    #if time[-1].lower() == "p" and hour < 12:
    #    hour += 12
    #dt = datetime.datetime(year, month, day, hour, minute, 0)
    #instr = ps[2].text.strip()[len("Instructor:"):]
    block = soup.find("div", attrs={"id":"spotwrapper"})
    #print "block: %s" % block
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
    #return dt, instr, unavail, total, occ
    return unavail, total, occ

def loginGetCookies(sitename):
    r = requests.get(LOGINGET[sitename], headers=USERAGENT, allow_redirects=True)
    cookies = r.cookies
    formdata = {'action': 'Account.doLogin', 'username': username, 'password':password}
    r = requests.post(LOGINPOST[sitename], data=formdata, headers=USERAGENT, cookies=cookies, allow_redirects=False)
    return cookies

def processSite(sitename, saveToDB=False):
    sum_unavail = sum_total = 0
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    cookies = loginGetCookies(sitename)
    #print cookies
    for item in getBookableLinks(sitename, cookies):
	#print item
        dt, instr, soldout, url = item
        if dt.date() > tomorrow:
            if sum_total:
                print "total occupancy: %d/%d = %.1f%%" % (sum_unavail, sum_total, float(sum_unavail)/sum_total*100.)
            break   
        if soldout:
            unavail = total = CAPACITY[sitename]
            occ = 100.
        else:
            unavail, total, occ = getOccupancy(sitename, url, cookies)
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
        sum_unavail += unavail
        sum_total += total
        if saveToDB:
            curs = conn.cursor()
            curs.execute("insert or replace into occ values (?, ?, ?, ?)", (dt, instr, unavail, total))
            conn.commit()

def main(saveToDB=False):
    for sitename in SITENAMES:
        print sitename
        processSite(sitename, saveToDB)
        print "-" * 80

if __name__ == "__main__":
    saveToDB = False
    if "-db" in sys.argv:
        saveToDB = True
    main(saveToDB)

