# Quick and dirty script to auto-tweet 
import os
import sys
import StringIO
import requests
import logging
import twitter
from BeautifulSoup import BeautifulSoup as BS
import datetime
secrets = open(".secret").read().strip().split(";")
baseurl, username, password, ckey, csec, akey, asec = secrets
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)

NDAYS = 1 
target_date = datetime.date.today() + datetime.timedelta(days=NDAYS)
starget_date = target_date.strftime("%a %b") + " " + str(target_date.day)

r = requests.get("http://www.%s/admin/" % baseurl, allow_redirects=True)
cookies = r.cookies
formdata = {'action': 'Sec.doLogin', 'username': username, 'password':password}
r = requests.post("http://www.%s/admin/index.cfm?action=" % baseurl, data=formdata, cookies=cookies, allow_redirects=False)
r = requests.get("http://www.%s/admin/index.cfm?action=Booker.view&roomid=1" % baseurl, cookies=cookies)
#open("/tmp/autotweet.html","w").write(r.text) 
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
while sib.text.count("-") >= 2:
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

if "-a" in sys.argv or (raw_input("tweet it? ").lower() == "y"):
    try:
        api.PostUpdate(tweet)
    except Exception as e:
        os.system("""echo "%s" | mail -s "autotweet FAILED" kevin.manley@gmail.com""" % (str(e)+" ("+tweet+")"))
    else:
        os.system("""echo "%s" | mail -s "autotweet SUCCESS" kevin.manley@gmail.com""" % tweet)

