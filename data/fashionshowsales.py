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

def fashionshow_sales():
	# quick hack to keep an eye on fashion show
	rows = list(conn.cursor().execute("select count(*)  from sale where item='VIP Ticket' and total='75.0';").fetchall())
	vip = rows[0][0]
	rows = list(conn.cursor().execute("select count(*)  from sale where item='General Admission' and total='50.0';").fetchall())
	genl = rows[0][0]
	total = genl + vip
	
	io = StringIO.StringIO()
	io.write("<html><body>")
	rows = list(conn.cursor().execute("select firstname, lastname, item, total, dt, pmtype from sale where (item='VIP Ticket' and total='75.0') or (item='General Admission' and total='50.0') order by lastname, firstname;").fetchall())
	if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>#</th><th>First name</th><th>Last Name</th><th>Ticket</th><th>Price</th><th>Purch Dt</th><th>Pmt Method</th></tr>")
		for i, row in enumerate(rows):
			firstname, lastname, item, price, dt, pmtype = row
			dt = dt[:16]
			io.write("<tr><td align='right'>%d</td><td>%s</td><td>%s</td><td>%s</td><td align='right'>%s</td><td>%s</td><td>%s</td></tr>" % \
			    (i+1, firstname, lastname, item, price, dt, pmtype))
		io.write("</table>")
	else:
		io.write("None")
	io.write("</body></html>")
	if dryRun:
		open(r"/tmp/test_fashionshowsales.html", "w").write(io.getvalue())
	else:
		send_report(io.getvalue(), "Joy of Art sales: %d General, %d VIP, %d Total" % (genl, vip, total), 
	              ['kevin@joyrideridgefield.com', 'amypal@joyrideridgefield.com'])

if __name__ == "__main__":
    fashionshow_sales()
