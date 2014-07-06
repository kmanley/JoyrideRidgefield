# Quick and dirty hack to check occupancy for a site where we don't have admin
import sys
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

SITENAMES = ["westport", "darien"]
SITES = {"westport":"http://www.%s/reserve/index.cfm?action=Reserve.chooseClass&site=1&n=Westport" % baseurl,
	 "darien":"http://www.%s/reserve/index.cfm?action=Reserve.chooseClass&site=3&n=Darien" % baseurl}

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
                    yield link.get("href")
	    else:
		pass #print "no link"

def getOccupancy(url, cookies):
    r = requests.get("http://www.%s%s" % (baseurl, url), headers=userAgent, cookies=cookies)
    soup = BS(r.text)
    details = soup.find("div", attrs={"class":"yui-u", "id":"sidebar"})
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

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
for sitename in SITENAMES[:1]:
    print sitename
    for url in getBookableLinks(sitename, cookies):
        #print url
        dt, instr, unavail, total, occ = getOccupancy(url, cookies)
        if dt.date() > tomorrow:
            break   
        print str(dt), instr, "%d/%d" % (unavail,total), "%.1f%%" % occ
	print "-" * 40
        

#r = requests.get("http://www.%s/reserve/index.cfm?action=Reserve.chooseSpot&classid=16601" % baseurl, cookies=cookies)

#print r.text.encode("utf-8")

"""
soup = BS(r.text)
lis = soup.findAll("li", attrs={"class":"nav-header"})
found = False
for li in lis:
    if li.text == starget_date:
        found = True
        break
if not found:
    log.warning("couldn't find target date %s" % starget_date)
    sys.exit(1)

classes = []
sib = li.findNextSibling()
while sib.text.count("-") == 2:
    parts = sib.text.split(" - ")
    if len(parts) != 3:
        log.warning("didn't find expected 3 part class description: %s" % sib.text)
        sys.exit(3)
    parts[0] = datetime.datetime.strptime(parts[0], "%I:%M %p")
    classes.append(parts)
    sib = sib.findNextSibling()

if not classes:
    log.warning("no classes found")
    sys.exit(2)

def format_tweet(dt, classes, inc_url=True):
    out = StringIO.StringIO()
    sdate = dt.strftime("%a").upper() + " " + ("%d/%d" % (dt.month, dt.day))
    out.write(sdate)
    out.write(": ")
    for i, (tm, instr, typ) in enumerate(classes):
        if i > 0:
            out.write(", ")
        hour = tm.hour
        if hour < 12:
            ampm = "a"
        else:
            ampm = "p"
            if hour > 12:
                hour -= 12
        if tm.minute:
            minute = ":%02d" % tm.minute
        else:
            minute = ""
        out.write(str(hour) + minute + ampm + " ")
        out.write(instr)
        if typ.lower() != "cycle":
            out.write(" (%s)" % typ)
    if inc_url:
        out.write(" ")
        out.write("%s/reserve" % baseurl)
  
    return out.getvalue()

# TODO: verify length < 140
tweet = format_tweet(target_date, classes)
print tweet

api = twitter.Api(consumer_key=ckey, consumer_secret=csec,
                  access_token_key=akey, 
                  access_token_secret=asec)
try:
    api.VerifyCredentials()
except Exception:
    log.exception("couldn't authenticate with Twitter")
    sys.exit(4)

if raw_input("tweet it? ").lower() == "y":
    api.PostUpdate(tweet)
"""
