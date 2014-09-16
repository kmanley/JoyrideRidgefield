import cStringIO as StringIO
from envelopes import Envelope, GMailSMTP
import getpass
import sqlite3
import datetime
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

dryRun = True
secrets = open(".mailreport-secret").read().strip().split(";")
TODAY = datetime.date.today()

conn = sqlite3.connect("joyridge.dat")

def get_firsttimers(offset=""):
    io = StringIO.StringIO()
    rows = conn.cursor().execute("select c.id, c.firstname, c.lastname, c.emailaddress, c.phone, c.phone2, a.classdate from attend a join cust c on a.custid=c.id  where a.num=1 and date(a.classdate)=date('now', 'localtime', '%s') order by classdate;" % offset).fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>First class</th></tr>")
    for i, row in enumerate(rows):
		_, firstname, lastname, email, phone1, _, classdate = row
		classdate = classdate[:16]
		io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %  (firstname + " " + lastname, email, phone1, classdate))
    io.write("</table>")
    return io.getvalue()

def get_toprecent(limit):
    io = StringIO.StringIO()
    rows = conn.cursor().execute("select * from vw_attendlast30 order by cnt desc limit ?", (limit,)).fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th># Rides</th></tr>")
    for i, row in enumerate(rows):
		_, firstname, lastname, email, phone1, _, cnt, frm, to = row
		io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, cnt))
    io.write("</table>")
    return io.getvalue()

def get_trending(direction, limit):
    io = StringIO.StringIO()
    rows = conn.cursor().execute("select * from vw_riderstrending%s limit ?" % direction, (limit,)).fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>T-60 to T-30</th><th>T-30 to T-0</th></tr>")
    for i, row in enumerate(rows):
		_, firstname, lastname, email, phone1, _, prev, last = row
		io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, prev, last))
    io.write("</table>")
    return io.getvalue()

def get_lapsed():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_riderslapsedtoday").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>T-60 to T-30</th><th>T-30 to T-0</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, prev = row
			io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, prev, 0))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_stalled():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select c.id, c.firstname, c.lastname, c.emailaddress, c.phone, " +
                                      "c.phone2, c.datecreated from cust c left outer join attend a " + 
                                      "on c.id=a.custid and a.status='Enrolled' where date(c.datecreated) " +
                                      "= date('now', '-7 days') and a.classdate is null and c.id not " +
                                      "in (select id from vw_fashionshowcusts) order by datecreated;").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Account Created</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, dt = row
			dt = dt[:16]
			io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %  (firstname.encode("ascii", "replace") + " " + lastname, email, phone1, dt))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_wallofjoy():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_milestonenext7").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Class date</th><th>Count</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, asof, cnt = row
			asof = asof[:16]
			if cnt % 100 == 0:
				io.write("<tr><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td align='right'><b>%d</b></td></tr>" %  (firstname + " " + lastname, email, phone1, asof, cnt))
			else:
				io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, asof, cnt))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_studiomilestones():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_studiomilestonenext7").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Class date</th><th>Rider Count</th><th>Studio Count</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, asof, ridercnt, studiocnt = row
			asof = asof[:16]
			if studiocnt % 10000 == 0:
				io.write("<tr><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td align='right'><b>%d</b></td><td align='right'><b>%d</b></td></tr>" %  (firstname + " " + lastname, email, phone1, asof, ridercnt, studiocnt))
			else:
				io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, asof, ridercnt, studiocnt))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_crazies():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_doublesthisweek order by firstclass;").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>First</th><th>Last</th><th>Count</th><th></th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, firstclass, lastclass, cnt = row
			firstclass = firstclass[:16]
			lastclass = lastclass[:16]
			if firstclass == lastclass:
				msg = "NOTE: %d spots in 1 class!" % cnt
			else:
				msg = ""
			io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td>%s</td></tr>" %  (firstname + " " + lastname, email, firstclass, lastclass, cnt, msg))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_birthdayriders():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_birthdaysthisweek v1 where v1.classdate is not null and v1.ndays = (select min(v2.ndays) from vw_birthdaysthisweek v2 where v2.id=v1.id);").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Birthday</th><th>Riding on</th></tr>")
		for i, row in enumerate(rows):
			#birthdate is actual historical day, birthday is that day this year
			_, firstname, lastname, email, phone1, _, birthdate, birthday, classday, _ = row
			birthdate = birthdate[:10]
			classday = classday[:16]
			if birthday[:10] == classday[:10]:
				io.write("<tr><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%s</b></td></tr>" %  (firstname + " " + lastname, email, phone1, birthdate, classday))
			else:
			    io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %  (firstname + " " + lastname, email, phone1, birthdate, classday))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def send_report(report, subj, recips=None): 
	recips = recips or ['frontdesk@joyrideridgefield.com', 'info@joyrideridgefield.com']
	envelope = Envelope(
	    from_addr=(u'joyride.robot@gmail.com', u'JoyRide Robot'),
	    to_addr=recips,
	    subject=subj,
	    html_body=report
	)

	log.info("sending email '%s' to '%s'" % (subj, repr(recips)))
	# Send the envelope using an ad-hoc connection...
	envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
					tls=True, port=587)

def rider_report():
	limit = 20
	io = StringIO.StringIO()
	io.write("<html><body>")
	io.write("<h3 style='margin:0px;'>Customers taking their first ride today</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: be sure to welcome them and give them any extra help they need</h4>")
	io.write(get_firsttimers('-0 days'))
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Customers who took their first ride yesterday</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: contact them <u>today</u>, get feedback, offer to sign them up for another class</h4>")
	io.write(get_firsttimers('-1 days'))
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Riders with birthdays in next 7 days</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: say Happy Birthday and tell them about birthday promotion</h4>")
	io.write(get_birthdayriders())
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Total studio rides</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: celebrate every 10,000th studio ride on social media</h4>")
	io.write(get_studiomilestones())
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Riders approaching Wall of Joy 100-ride milestone</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: celebrate every 100th customer rides on social media</h4>")
	io.write(get_wallofjoy())
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Riders doing doubles this week (or booking multiple spots in a class)</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: hat tip to double-riders; please investigate/correct multiple bookings under same name</h4>")
	io.write(get_crazies())
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Top %d riders over past 30 days</h3>" % limit)
	io.write("<h4 style='margin:0px;'>ACTION: extra care & attention; these are our best riders lately</h4>")	
	io.write(get_toprecent(limit))
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Top %d up-trending riders over past 30 days</h3>" % limit)
	io.write("<h4 style='margin:0px;'>ACTION: let them know you've noticed how hard they're working</h4>")		
	io.write(get_trending("up", limit))
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Top %d down-trending riders over past 30 days</h3>" % limit)
	io.write("<h4 style='margin:0px;'>ACTION: encourage them, if possible determine if there are any problems/issues</h4>")	
	io.write(get_trending("down", limit))
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>Riders lapsed as of today</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: contact them <u>today</u>, determine if any problems/issues, try to win back their business</h4>")	
	io.write(get_lapsed())
	io.write("<p/>")
	io.write("<h3 style='margin:0px;'>New customers who never enrolled in a class</h3>")
	io.write("<h4 style='margin:0px;'>ACTION: contact them <u>today</u>, try to sign them up for a class</h4>")	
	io.write(get_stalled())
	io.write("<p/>Best regards,<br/>JoyRide Robot")
	io.write("</body></html>")
	if dryRun:
		with open("/tmp/test.html","wb") as fp:
			fp.write(io.getvalue())    
	else:
		send_report(io.getvalue(), 'Rider report for %s' % str(TODAY))

if __name__ == "__main__":
    rider_report()
