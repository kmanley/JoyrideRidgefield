import cStringIO as StringIO
from envelopes import Envelope, GMailSMTP
import getpass
import sqlite3
import datetime

secrets = open(".mailreport-secret").read().strip().split(";")
TODAY = datetime.date.today()

conn = sqlite3.connect("joyridge.dat")

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
    rows = list(conn.cursor().execute("select * from vw_riderslapsed limit ?", (limit,)).fetchall())
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
    rows = list(conn.cursor().execute("select * from vw_wallofjoy").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th># Classes</th><th>As of</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, cnt, asof = row
			io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td>%s</td></tr>" %  (firstname + " " + lastname, email, phone1, cnt, asof))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def get_birthdayriders():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_birthdaysthisweek where classdate is not null").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Birthday</th><th>Riding on</th></tr>")
		for i, row in enumerate(rows):
			#birthdate is actual historical day, birthday is that day this year
			_, firstname, lastname, email, phone1, _, birthdate, birthday, classday = row
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
	    to_addr=['kevin@joyrideridgefield.com', 'amypal@joyrideridgefield.com'],
	    subject=subj,
	    html_body=report
	)

	# Send the envelope using an ad-hoc connection...
	envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
					tls=True, port=587)

def main():
	limit = 25
	io = StringIO.StringIO()
	io.write("<html><body>")
	io.write("<h4>Top %d riders trending up</h4>" % limit)
	io.write(get_trending("up", limit))
	io.write("<h4>Top %d riders trending down</h4>" % limit)
	io.write(get_trending("down", limit))
	io.write("<h4>Top %d riders recently lapsed</h4>" % limit)
	io.write(get_lapsed(limit))
	io.write("<h4>Riders approaching Wall of Joy milestone</h4>")
	io.write(get_wallofjoy())
	io.write("<h4>Riders with birthdays this week</h4>")
	io.write(get_birthdayriders())
	io.write("</body></html>")
	#send_report(io.getvalue(), 'Rider report for %s' % str(TODAY))
	with open("/tmp/test.html","wb") as fp:
		fp.write(io.getvalue())    

if __name__ == "__main__":
    main()
