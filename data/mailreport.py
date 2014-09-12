import cStringIO as StringIO
from envelopes import Envelope, GMailSMTP
import getpass
import sqlite3
import datetime

dryRun = False
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

def get_lapsed(limit):
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


def send_report(report, subj):
	envelope = Envelope(
	    from_addr=(u'joyride.robot@gmail.com', u'JoyRide Robot'),
	    to_addr=['frontdesk@joyrideridgefield.com', 'info@joyrideridgefield.com'],
            #to_addr=['kevin.manley@gmail.com'],
	    subject=subj,
	    html_body=report
	)

	# Send the envelope using an ad-hoc connection...
	envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
					tls=True, port=587)

def main():
	limit = 20
	io = StringIO.StringIO()
	io.write("<html><body>")
	io.write("Good morning!<br/>")
	io.write("<h4>Customers taking their first ride today (help them out!)</h4>")
	io.write(get_firsttimers('-0 days'))
	io.write("<h4>Customers who took their first ride yesterday (follow up--did they like it? want to buy a package?)</h4>")
	io.write(get_firsttimers('-1 days'))
	io.write("<h4>Riders with birthdays in next 7 days</h4>")
	io.write(get_birthdayriders())
	io.write("<h4>Total studio rides (celebrate milestones like 20k, 30k, etc)</h4>")
	io.write(get_studiomilestones())
	io.write("<h4>Riders approaching Wall of Joy 100-ride milestone</h4>")
	io.write(get_wallofjoy())
	io.write("<h4>Riders doing doubles this week (or booking multiple spots in a class)</h4>")
	io.write(get_crazies())
	io.write("<h4>Top %d riders over past 30 days</h4>" % limit)
	io.write(get_toprecent(limit))
	io.write("<h4>Top %d up-trending riders over past 30 days</h4>" % limit)
	io.write(get_trending("up", limit))
	io.write("<h4>Top %d down-trending riders over past 30 days</h4>" % limit)
	io.write(get_trending("down", limit))
	io.write("<h4>Riders lapsed as of today. Please contact them!</h4>")
	io.write(get_lapsed(limit))
	io.write("<br/>Best regards,<br/>JoyRide Robot")
	io.write("</body></html>")
	if dryRun:
		with open("/tmp/test.html","wb") as fp:
			fp.write(io.getvalue())    
	else:
		send_report(io.getvalue(), 'Rider report for %s' % str(TODAY))

if __name__ == "__main__":
    main()
