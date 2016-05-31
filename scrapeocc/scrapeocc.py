# Quick and dirty hack to check occupancy for sites where we don't have admin
import sys
import sqlite3
import StringIO
import requests
import logging
import twitter
import subprocess
#from BeautifulSoup import BeautifulSoup as BS
from bs4 import BeautifulSoup as BS
import datetime
secrets = open(".secret").read().strip().split(";")
username, password = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True

conn = sqlite3.connect("occupancy.db")

SITENAMES = ["wilton", "wilton2", "westport", "westport2", "darien", "darien2", "ridgefield", "texas-bdwy", "texas-alon", "texas-alon2",
             "studio22", "shiftg", "shiftnh", "zenride", "tribe", "scgreenwich", "scwestport"]

BASEURL = { "wilton" : "http://www.joyridestudio.com",
           "wilton2" : "http://www.joyridestudio.com",
          "westport" : "http://www.joyridestudio.com",
           "westport2" : "http://www.joyridestudio.com",
           "darien" : "http://www.joyridestudio.com",
           "darien2" : "http://www.joyridestudio.com",
           "ridgefield" : "http://www.joyridestudio.com",
           "texas-bdwy" : "http://www.joyridestudio.com",
           "texas-alon" : "http://www.joyridestudio.com",
           "texas-alon2" : "http://www.joyridestudio.com",
           "studio22" : "http://www.studio22fitness.com",
           "shiftg" : "http://www.shiftcycling.com",
           "shiftnh" : "http://www.shiftcycling.com",
           "zenride" : "http://www.zen-ride.com",
           "tribe" : "http://www.unitethetribe.com",
           "scgreenwich" : "http://www.soul-cycle.com",
           "scwestport" : "http://www.soul-cycle.com",
   }

USERAGENT = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36"}

LOGINGET = {"westport"  :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "westport2"  :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "darien"    :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "darien2"    :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "ridgefield":  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
            "wilton":  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
            "wilton2":  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
            "texas-bdwy"     :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
	    "texas-alon"     :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
            "texas-alon2"     :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",  
            "studio22"  :  "http://www.studio22fitness.com/reserve/index.cfm?action=Account.login", 
            "shiftg"  :  "http://www.shiftcycling.com/reserve/index.cfm?action=Account.login", 
            "shiftnh"  :  "http://www.shiftcycling.com/reserve/index.cfm?action=Account.login", 
            "zenride"  :  "http://www.zen-ride.com/reserve/index.cfm?action=Account.login", 
            "tribe" : "http://www.unitethetribe.com/reserve/index.cfm?action=Account.login", 
            }

LOGINPOST = {"westport" : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "westport2" : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "darien"    : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "darien2"    : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "ridgefield": "http://www.joyridestudio.com/reserve/index.cfm?action=", 
            "wilton": "http://www.joyridestudio.com/reserve/index.cfm?action=", 
            "wilton2": "http://www.joyridestudio.com/reserve/index.cfm?action=", 
            "texas-bdwy"     : "http://www.joyridestudio.com/reserve/index.cfm?action=",
            "texas-alon"     : "http://www.joyridestudio.com/reserve/index.cfm?action=", 
            "texas-alon2"     : "http://www.joyridestudio.com/reserve/index.cfm?action=",  
            "studio22"  : "http://www.studio22fitness.com/reserve/index.cfm?action=", 
            "shiftg"    : "http://www.shiftcycling.com/reserve/index.cfm?action=", 
            "shiftnh"   : "http://www.shiftcycling.com/reserve/index.cfm?action=", 
            "zenride"   : "http://www.zen-ride.com/reserve/index.cfm?action=", 
            "tribe"     : "http://www.unitethetribe.com/reserve/index.cfm?action=", 
            }

CALENDARGET = {"westport": "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&roomid=1", 
               "westport2": "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&roomid=3", 
               "darien":    "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien&roomid=5",
               "darien2":    "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien&roomid=6",
               "ridgefield":"http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=5&roomid=10",
               "wilton": "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=7&roomid=13",
               "wilton2": "http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=7&roomid=18",
               "texas-bdwy":"http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=6&roomid=12",
               "texas-alon":"http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=8&roomid=15",
               "texas-alon2":"http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=8&roomid=16",
               "studio22":"http://www.studio22fitness.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&roomid=1",
               "shiftg": "http://www.shiftcycling.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               "shiftnh":"http://www.shiftcycling.com/reserve/index.cfm?action=Reserve.chooseClass&site=2",
               "zenride":"http://www.zen-ride.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               "tribe" : "http://www.unitethetribe.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               } 

CAPACITY = {"westport":46, 
            "westport2":20,
            "wilton":36,
            "wilton2":10,
            "darien":40, 
            "darien2":20,
            "ridgefield":44,
            "texas-bdwy":35,
            "texas-alon":34,
            "texas-alon2":11,
            "studio22":32,
            "shiftg":29,
            "shiftnh":39,
            "scgreenwich":60,
            "scwestport":56,
            "zenride":36,
            "tribe":34}

TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
#TODAY = TOMORROW

# TODO: sold out classes (classfull class) have a link that does not contain date/time info, just a "sorry, class full msg"
# so we need to extract date/time/instructor here instead of in getOccupancy
def getBookableLinksZingfit(site, cookies):
    url = CALENDARGET[site]
    log.info("requesting %s" % url)
    r = requests.get(url, headers=USERAGENT, cookies=cookies)
    #open("/tmp/tribe.html", "w").write(r.text) # TODO:
    soup = BS(r.text) #, "html.parser")
    blocks = soup.findAll("div", attrs={"class":["scheduleBlock", "scheduleBlock classfull"]})
    #print "%d blocks" % len(blocks)
    for block in blocks:
        link = block.find("a")
        if link:
        #    classtype = link.span.text.lower()
        # we changed links to filter by room, so don't have to guess if it's a cycle class based on name anymore
            if True:
            #if ("cycle" in classtype) or ("tabata" in classtype) or ("ride" in classtype) or (site=="ridgefield"):
                #print link.parent.parent["class"]
                if site=="tribe":
                    #print link.parent.parent["id"]
                    sdate = link.parent.parent["id"]
                    day = int(sdate[9:])
                    month = int(sdate[7:9])
                    #print "!!!", month, day
                    instr = block.find("span", attrs={"class":"scheduleInstruc"}).text.strip()
                    stime = block.find("span", attrs={"class":"scheduleTime"}).text.strip()
                else:
                    day = int(link.parent.parent["class"][0][3:].split(" ")[0])
                    sdate = soup.findAll("span", attrs={"class":"thead-date"})[day].text
                    dateparts = sdate.split(".")
                    month = int(dateparts[0])
                    day = int(dateparts[1])
                    instr = block.find("span", attrs={"class":"scheduleInstruc active"}).text.strip()
                    stime = block.find("span", attrs={"class":"scheduleTime active"}).text.strip()
                # 11:00 AM60min
                hour = int(stime.split(":")[0])
                minute = int(stime.split(" ")[0].split(":")[-1])
                if stime.split(" ")[1].startswith("PM") and hour < 12:
                    hour += 12
                if " ".join(block["class"]).find("classfull") > -1:
                    soldout = True
                else:
                    soldout = False
                
                year = (datetime.date(TODAY.year, TODAY.month, 1) + datetime.timedelta(days=day-1)).year
                if datetime.date(year, month, day) < TODAY:
                    year += 1
                dt = datetime.datetime(year, month, day, hour, minute, 0)
                #print dt, instr, soldout, link.get("href")
                yield dt, instr, soldout, link.get("href")
        else:
            pass #not bookable - class is in past or cancelled

def getOccupancyZingfit(site, url, cookies):
    r = requests.get("%s%s" % (BASEURL[site], url), headers=USERAGENT, cookies=cookies)
    soup = BS(r.text)
    block = soup.find("div", attrs={"id":"spotwrapper"})
    avail = 0
    unavail = 0
    for item in block:
        if not hasattr(item, "name"):
            continue
        if item.name == "span":
            # span class is "spotcell Enrolled" for real booking
            # it's "spotcell Unavailable" for held spot; we only count real bookings
            if "".join(item["class"]).lower().find("enrolled")>-1:
                unavail += 1
            else:
                avail += 1
        elif item.name == "a":
            avail += 1
    total = avail + unavail
    occ = float(unavail) / total * 100.
    return unavail, total, occ

def loginGetCookies(sitename):
    r = requests.get(LOGINGET[sitename], headers=USERAGENT, allow_redirects=True)
    cookies = r.cookies
    formdata = {'action': 'Account.doLogin', 'username': username, 'password':password}
    r = requests.post(LOGINPOST[sitename], data=formdata, headers=USERAGENT, cookies=cookies, allow_redirects=False)
    return cookies

def processSiteZingfit(sitename, saveToDB=False):
    sum_unavail = sum_total = 0
    cookies = loginGetCookies(sitename)
    for item in getBookableLinksZingfit(sitename, cookies):
        #print "item",  item # TODO:
        dt, instr, soldout, url = item
        if dt.date() > TOMORROW:
            #print "breaking because %s > %s" % (dt.date(), TOMORROW)
            break   
        if soldout:
            unavail = total = CAPACITY[sitename]
            occ = 100.
        else:
            unavail, total, occ = getOccupancyZingfit(sitename, url, cookies)
        if total < CAPACITY[sitename]:
            # ktm 15 dec 14 - zingfit bug means we can no longer filter by room, so we get everything. only way to know
            # if it's non-cycle is to check room size, but that won't work if the non-cycle class is sold out. luckily they
            # don't seem to sell out.
            continue
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
        if saveToDB:
            curs = conn.cursor()
            #curs.execute("insert or ignore into occ (dt, site) values (?, ?)", (dt, sitename))
            #curs.execute("update occ set instr=?, unavail=?, total=? where dt=? and site=?", (instr, unavail, total, dt, sitename))
            curs.execute("delete from occ where dt=? and site=?", (dt, sitename))
            curs.execute("insert into occ (dt, site, instr, unavail, total) values (?, ?, ?, ?, ?)", (dt, sitename, instr, unavail, total))
            conn.commit()

def processSiteSC(sitename, saveToDB=False):
    for dt, instr, _, url in getBookableLinksSC(sitename, saveToDB):
        unavail, total, occ = getOccupancySC(sitename, url)
        #print unavail, total, occ
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
        if saveToDB:
            curs = conn.cursor()
            curs.execute("delete from occ where dt=? and site=?", (dt, sitename))
            curs.execute("insert into occ (dt, site, instr, unavail, total) values (?, ?, ?, ?, ?)", (dt, sitename, instr, unavail, total))
            conn.commit()
        
"""
def getOccupancySC(site, url):
    r = requests.get("%s%s" % (BASEURL[site], url), headers=USERAGENT)
    #open(r"/tmp/scwtf.html","w").write(r.text) # TODO:
    print r.text
    #soup = BS(r.text)
    #avail = len(soup.findAll("div", attrs={"class":["seat", "open"]}))
    #unavail = len(soup.findAll("div", attrs={"class":["seat", "taken"]}))
    if r.text.lower().find("the class you requested is full") >= 0:
        avail = 0
        unavail = CAPACITY[site]
    else:
        avail = r.text.count("seat open")
        print "***** avail: ", avail
        unavail = CAPACITY[site] - avail
    total = avail + unavail
    occ = float(unavail) / total * 100.
    sys.exit(0)
    return unavail, total, occ
"""
def getOccupancySC(site, url):
        print "getOccupancySC: %s%s" % (BASEURL[site],url)
	res = subprocess.check_output(["phantomjs", "--ssl-protocol=any", "getscocc.js", "%s%s" % (BASEURL[site],url)])
	unavail = int(res)
	if unavail < 0:
		# the js script signals sold out by emitting -1 to stdout
		unavail = CAPACITY[site]
	avail = CAPACITY[site] - unavail
	total = avail + unavail
	occ = float(unavail) / total * 100.
	return unavail, total, occ
    
def getBookableLinksSC(sitename, saveToDB=False):
    SCHEDULEURLS = {"scgreenwich":"https://www.soul-cycle.com/find-a-class/studio/212/",
                    "scwestport":"https://www.soul-cycle.com/find-a-class/studio/1026/"}
    url = SCHEDULEURLS[sitename]
    print "get %s" % url
    r = requests.get(url, headers=USERAGENT, timeout=10)
    print "got here"
    #open(r"/tmp/sc.html", "w").write(r.text.encode("utf-8"))
    #print r.text
    #print "got here"
    soup = BS(r.text)
    #dt = TOMORROW.strftime("%b %d, %Y")
    now = datetime.datetime.now()
    blocks = soup.findAll("div", attrs={"class":["session", "open"]})
    for block in blocks:   
        #print block.parent.parent
        day = int(block.parent.parent["data-date"])
        #print "***", day
        if day >= TODAY.day:
            dt = datetime.date(TODAY.year, TODAY.month, day)
        else:
            dt = datetime.date(TODAY.year if TODAY.month < 12 else TODAY.year+1, (TODAY.month+1)%12, day)
        
        #dt = datetime.datetime.strptime(sdt, "%B %d, %Y")
        
        #print "***", dt
        stm = block.find("span", attrs={"class":"time"}).text
        #print "***", stm
        hh = int(stm.split(":")[0])
        mm = int(stm.split(":")[-1][:2])
        ampm = stm[-2:]
        if ampm=="PM" and hh < 12:
            hh += 12
        instr = block.find("span", attrs={"class":"instructor"}).text.strip()
        dt = datetime.datetime(dt.year, dt.month, dt.day, hh, mm)
        url = block.find("a", attrs={"class":["open-modal", "reserve"]})
        if url:
            url = url["href"]
        if dt >= now and dt.date() <= TOMORROW:
            #print dt, instr, url
            yield dt, instr, False, url
    

def main(saveToDB=False, site=None):
    sitenames = [site] if site else SITENAMES
    for sitename in sitenames:
        print sitename
        if sitename in ("scgreenwich", "scwestport"):
            processSiteSC(sitename, saveToDB)
        else:
            processSiteZingfit(sitename, saveToDB)
        print "-" * 80

if __name__ == "__main__":
    sitename = None
    if len(sys.argv) > 1 and sys.argv[1].find("-d") < 0:
        sitename = sys.argv[1].lower().strip()
    saveToDB = False
    if sys.argv[-1].find("-d") > -1:
        print "will save to db"
        saveToDB = True
    main(saveToDB, sitename)

