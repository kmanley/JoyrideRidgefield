"""
For series, there is breakage due to non-usage as well as expiry
It's hard to model as a liability
"""

import csv
import math
import datetime

allmonthlies = {}
pastmonthlies = {}
currmonthlies = {}
today = datetime.date.today()
totexpected = 0.0
monthlyprice = 199.99

with open('/home/kevin/Downloads/jrr-monthlies.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for i, row in enumerate(reader):
        if i==0:
            continue # skip header
        #totmonthlies += 1
        allmonthlies[row[4]] = allmonthlies.get(row[4],0) + 1
        expiry = datetime.datetime.strptime(row[-4][:10], "%Y-%m-%d").date()
        if expiry >= today:
            currmonthlies[row[4]] = 0

pastmonthlies = dict([(x,0) for x in allmonthlies if x not in currmonthlies])        
#avgtenure = int(math.ceil((float(totmonthlies) / len(allmonthlies))))
avgtenurepast = float(sum([allmonthlies[x] for x in pastmonthlies])) / len(pastmonthlies)
avgtenurecurr = float(sum([allmonthlies[x] for x in currmonthlies])) / len(currmonthlies)
        
print "# people who've ever had monthlies: %d" % len(allmonthlies)
print "# people who have expired: %d" % len(pastmonthlies)
print "avg tenure of expired members: %.2f months" % avgtenurepast
print "# people who currently have monthlies: %d" % len(currmonthlies)
print "avg tenure of current members: %.2f months" % avgtenurecurr

for name in currmonthlies.keys():
    count = allmonthlies[name]
    print "%s has %s months" % (name, count)
    if count < avgtenurepast:
        expected = (avgtenurepast - count) * monthlyprice
        totexpected += expected
        print "  assume will expire; expect %.2f more revenue from %s" % (expected, name)
    elif count < avgtenurecurr:
        expected = (avgtenurecurr - count) * monthlyprice
        print "  assume will achieve curr avg; expect %.2f more revenue from %s" % (expected, name)
        totexpected += expected
    else:
        expected = monthlyprice * count * .2 # TODO: .2?
        print "  assume will exceed avg; expect %.2f more revenue from %s" % (expected, name)
        totexpected += expected
        
        
print "total expected future revenue: %.2f" % totexpected
