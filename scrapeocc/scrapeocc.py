# Quick and dirty hack to check occupancy for sites where we don't have admin
import sys
import sqlite3
import StringIO
import requests
import logging
import twitter
#from BeautifulSoup import BeautifulSoup as BS
from bs4 import BeautifulSoup as BS
import datetime
secrets = open(".secret").read().strip().split(";")
username, password = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)

conn = sqlite3.connect("occupancy.db")

SITENAMES = ["westport", "westport2", "darien", "darien2", "ridgefield", "texas", 
             "studio22", "shiftg", "shiftnh", "zenride", "tribe"] # TODO: scwestport

BASEURL = {"westport" : "http://www.joyridestudio.com",
           "westport2" : "http://www.joyridestudio.com",
           "darien" : "http://www.joyridestudio.com",
           "darien2" : "http://www.joyridestudio.com",
           "ridgefield" : "http://www.joyridestudio.com",
           "texas" : "http://www.joyridestudio.com",
           "studio22" : "http://www.studio22fitness.com",
           "shiftg" : "http://www.shiftcycling.com",
           "shiftnh" : "http://www.shiftcycling.com",
           "zenride" : "http://www.zen-ride.com",
           "tribe" : "http://www.unitethetribe.com",
   }

USERAGENT = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}

LOGINGET = {"westport"  :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "westport2"  :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "darien"    :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "darien2"    :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login",
            "ridgefield":  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
            "texas"     :  "http://www.joyridestudio.com/reserve/index.cfm?action=Account.login", 
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
            "texas"     : "http://www.joyridestudio.com/reserve/index.cfm?action=", 
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
               "texas":"http://www.joyridestudio.com/reserve/index.cfm?action=Reserve.chooseClass&site=6&roomid=12",
               "studio22":"http://www.studio22fitness.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&roomid=1",
               "shiftg": "http://www.shiftcycling.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               "shiftnh":"http://www.shiftcycling.com/reserve/index.cfm?action=Reserve.chooseClass&site=2",
               "zenride":"http://www.zen-ride.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               "tribe" : "http://www.unitethetribe.com/reserve/index.cfm?action=Reserve.chooseClass&site=1",
               } 

CAPACITY = {"westport":46, 
            "westport2":20,
            "darien":40, 
            "darien2":20,
            "ridgefield":44,
            "texas":35,
            "studio22":32,
            "shiftg":29,
            "shiftnh":39,
            "scwestport":56,
            "zenride":36,
            "tribe":34}

TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
#TODAY = TOMORROW

# TODO: sold out classes (classfull class) have a link that does not contain date/time info, just a "sorry, class full msg"
# so we need to extract date/time/instructor here instead of in getOccupancy
def getBookableLinks(site, cookies):
    url = CALENDARGET[site]
    log.info("requesting %s" % url)
    r = requests.get(url, headers=USERAGENT, cookies=cookies)
    #open("/tmp/tribe.html", "w").write(r.text) # TODO:
    soup = BS(r.text) #, "html.parser")
    blocks = soup.findAll("div", attrs={"class":["scheduleBlock", "scheduleBlock classfull"]})
    #print "%d blocks" % len(blocks)
    for block in blocks:
        #print "*" * 50
        #print block
        #print "*"
        #print
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
                    instr = block.find("span", attrs={"class":"scheduleInstruc"}).text
                    stime = block.find("span", attrs={"class":"scheduleTime"}).text
                else:
                    day = int(link.parent.parent["class"][0][3:].split(" ")[0])
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

def getOccupancy(site, url, cookies):
    #print "getOcc %s" % url
    #print "%s%s" % (BASEURL[site], url)
    #print cookies
    r = requests.get("%s%s" % (BASEURL[site], url), headers=USERAGENT, cookies=cookies)
    #open("class_example.html","wb").write(r.text)
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
    #return dt, instr, unavail, total, occ
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
    lastdt = None
    for item in getBookableLinks(sitename, cookies):
        #print "item",  item # TODO:
        dt, instr, soldout, url = item
        if lastdt and dt.date() > lastdt:
            # NOTE: it's *remaining* occupancy for today since it's only correct for the whole day until the point the first
            # class starts (because after that we can't scrape that class anymore). Better to use db for aggregations
            if sum_total:
                if lastdt == TODAY:
                    prefix = "remaining "
                else:
                    prefix = ""
                print "%soccupancy for %s: %d/%d = %.1f%%" % (prefix, lastdt, sum_unavail, 
            sum_total, float(sum_unavail)/sum_total*100.)
            print
            sum_unavail = sum_total = 0
        if dt.date() > TOMORROW:
            #print "breaking because %s > %s" % (dt.date(), TOMORROW)
            break   
        lastdt = dt.date()
        if soldout:
            unavail = total = CAPACITY[sitename]
            occ = 100.
        else:
            unavail, total, occ = getOccupancy(sitename, url, cookies)
        if total < CAPACITY[sitename]:
            # ktm 15 dec 14 - zingfit bug means we can no longer filter by room, so we get everything. only way to know
            # if it's non-cycle is to check room size, but that won't work if the non-cycle class is sold out. luckily they
            # don't seem to sell out.
            continue
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
        sum_unavail += unavail
        sum_total += total
        if saveToDB:
            curs = conn.cursor()
            #curs.execute("insert or ignore into occ (dt, site) values (?, ?)", (dt, sitename))
            #curs.execute("update occ set instr=?, unavail=?, total=? where dt=? and site=?", (instr, unavail, total, dt, sitename))
            curs.execute("delete from occ where dt=? and site=?", (dt, sitename))
            curs.execute("insert into occ (dt, site, instr, unavail, total) values (?, ?, ?, ?, ?)", (dt, sitename, instr, unavail, total))
            conn.commit()

def processSiteSC(sitename, saveToDB=False):
    getBookableLinksSC(sitename, saveToDB)
    
    
def getBookableLinksSC(sitename, saveToDB=False):
    SCHEDULEURLS = {"scwestport":"https://www.soul-cycle.com/find-a-class/studio/1026/"}
    url = SCHEDULEURLS[sitename]
    r = requests.get(url, headers=USERAGENT)
    #open(r"/tmp/sc.html", "w").write(r.text.encode("utf-8"))
    soup = BS(r.text)
    dt = TOMORROW.strftime("%b %d, %Y")
    blocks = soup.findAll("div", attrs={"class":["column-day "]})
    for block in blocks:   
        if block["data-date"] == dt:
            times = block.findAll("span", attrs={"class":["time"]})
            for time in times:
                hh = int(time.text.split(":")[0])
                mm = int(time.text.split(":")[-1][:2])
                ampm = time.text.split(":")[-1][-2:]
                if ampm == "PM":
                    hh += 12
                #print hh, mm
                dt = datetime.datetime(TOMORROW.year, TOMORROW.month, TOMORROW.day,
                                        hh, mm, 0)
                instr = time.nextSibling().findAll("a")[0].text
                #instr = time.nextSibling()
                #.findAll("a")[0].text
                
                print time, dt, instr
            #print block
    
    #yield dt, instr, soldout, link.get("href")


def main(saveToDB=False, site=None):
    sitenames = [site] if site else SITENAMES
    for sitename in sitenames:
        print sitename
        if sitename=="scwestport":
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

