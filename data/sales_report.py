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

def get_custalltime():
    io = StringIO.StringIO()
    rows = list(conn.cursor().execute("select * from vw_customersalesalltime limit 20").fetchall())
    if rows:
		io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
		io.write("<tr><th>Name</th><th>Email</th><th>Phone</th><th>Num Txs</th><th>Total spend</th></tr>")
		for i, row in enumerate(rows):
			_, firstname, lastname, email, phone1, _, numtx, spend = row
			io.write(("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td></tr>" %  (firstname + " " + lastname, email, phone1, numtx, spend)).encode('utf-8', 'replace'))
		io.write("</table>")
    else:
		io.write("None")
    return io.getvalue()

def send_report(report, subj, recips=None): 
	recips = recips or ['kevin.manley@gmail.com'] # TODO: ['frontdesk@joyrideridgefield.com', 'info@joyrideridgefield.com']
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

def sales_report():
	limit = 20
	io = StringIO.StringIO()
	io.write("<html><body>")
	io.write("<h3 style='margin:0px;'>Top customers by spend (all time)</h3>")
	io.write(get_custalltime())
	io.write("<p/>")
	io.write("<p/>Best regards,<br/>JoyRide Robot")
	io.write("</body></html>")
	if dryRun:
		with open("/tmp/test.html","wb") as fp:
			fp.write(io.getvalue())    
	else:
		send_report(io.getvalue(), 'Sales report for %s' % str(TODAY))

if __name__ == "__main__":
    sales_report()
