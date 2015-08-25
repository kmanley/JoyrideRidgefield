# Quick and dirty script to auto-tweet 
# NOTE: uses python-twitter module (sudo pip install python-twitter)
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
log.setLevel(logging.WARNING)

NDAYS = 1
target_date = datetime.date.today() + datetime.timedelta(days=NDAYS)
starget_date = target_date.strftime("%a %b") + " " + str(target_date.day)

site = sys.argv[1] if len(sys.argv)>1 else None
if site=="ridgefield":
    # Ridgefield
    siteid=5
    roomid=10
    studiodomain="joyrideridgefield.com"
    secrets = ".secret-ridgefield"
elif site=="wilton":
    # Wilton
    siteid=7
    roomid=13
    studiodomain="joyridewilton.com"
    secrets = ".secret-wilton"
else:
    raise Exception("expected site param 'ridgefield' or 'wilton'")

secrets = open(secrets).read().strip().split(";")
baseurl, username, password, ckey, csec, akey, asec = secrets

r = requests.get("http://www.%s/admin/" % baseurl, allow_redirects=True)
cookies = r.cookies
formdata = {'action': 'Sec.doLogin', 'username': username, 'password':password}
r = requests.post("http://www.%s/admin/index.cfm?action=" % baseurl, data=formdata, cookies=cookies, allow_redirects=False)
# set site cookie and get booker view
r = requests.get(r"http://www.%s/admin/index.cfm?action=Register.setSite&siteid=%s" % (baseurl, siteid), cookies=cookies, allow_redirects=False)
#&returnurl=%%2Fadmin%%2Findex%%2Ecfm%%3Faction%%3DBooker%%2Eview&amp;roomid%%3D%s" % (baseurl, siteid, roomid), cookies=r.cookies, allow_redirects=True)
r = requests.get("http://www.%s/admin/index.cfm?action=Booker.view&roomid=%s" % (baseurl, roomid), cookies=cookies)
#open("/tmp/autotweet.html","w").write(r.text) 
soup = BS(r.text)
lis = soup.findAll("h5", attrs={"class":"nav-header"})
found = False
for li in lis:
    #print li.text
    if li.text == starget_date:
        found = True
        break
if not found:
    log.warning("couldn't find target date %s" % starget_date)
    sys.exit(1)

classes = []
sublis = li.findNextSibling().findAll("li")
for subli in sublis: #while sib.text.count("-") >= 2:
    parts = subli.text.split(" - ", 2)
    if len(parts) != 3:
        log.warning("didn't find expected 3 part class description: %s" % subli.text)
        sys.exit(3)
    parts[0] = datetime.datetime.strptime(parts[0], "%I:%M %p")
    classes.append(parts)
    #sib = sib.findNextSibling()

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
    if inc_url and len(out.getvalue()) <= 118:
        #t.co links are 22 chars, 118+22 = 140 max
        out.write(" ")
        out.write("%s/reserve" % studiodomain)
  
    return out.getvalue()

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

if "-a" in sys.argv or (raw_input("tweet it? ").lower() == "y"):
    try:
        api.PostUpdate(tweet)
    except Exception as e:
        log.exception("failed to post update to Twitter")
        os.system("""echo "%s" | mail -s "autotweet FAILED" -r "noreply-root@joyrd.link" kevin.manley@gmail.com""" % (str(e)+" ("+tweet+")"))
    else:
        log.info("successfully posted to Twitter")
        os.system("""echo "%s" | mail -s "autotweet SUCCESS" -r "noreply-root@joyrd.link" kevin.manley@gmail.com""" % tweet)

