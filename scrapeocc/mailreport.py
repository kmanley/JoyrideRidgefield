import cStringIO as StringIO
from envelopes import Envelope, GMailSMTP
import getpass
import sqlite3
import datetime

dryRun = False

secrets = open(".mailreport-secret").read().strip().split(";")
TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)

conn = sqlite3.connect("occupancy.db")

def get_table(dt):
    io = StringIO.StringIO()
    #curs = conn.cursor()
    rows = list(conn.cursor().execute("select * from v_occ where date(dt) = ? order by case when site='ridgefield' then 1 when site='wilton' then 2 when site='westport' then 3 when site='darien' then 4 when site='texas' then 5 when site='westport2' then 6 when site='darien2' then 7 else site end, dt;", (dt,)).fetchall())
    #rows = curs.fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Date/time</th><th>Studio</th><th>Instr/Count</th><th>Sold</th><th>Total</th><th>Occ%</th></tr>")
    for i, row in enumerate(rows):
        row = list(row) # so we can edit it
        # strip off seconds
        row[0] = row[0][:-3]
        row = tuple(row) 
        io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%.2f%%</td></tr>" % row)
		# if site is about to change or we're at the end, show summary
        if i==len(rows)-1 or rows[i+1][1] != row[1]:
            summrow = conn.cursor().execute("select * from v_date where dt=? and site=?", (dt,row[1])).fetchone()
            io.write("<tr><td>%s</td><td>%s</td><td>%d classes</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%.2f%%</td></tr>" % summrow)
            if i < len(rows)-1:
                io.write("<tr><td colspan='6' bgcolor='#aaaaaa'/></tr>")
    io.write("</table>")
    return io.getvalue()
    
def get_history_by_studio():
    io = StringIO.StringIO()
    #curs = conn.cursor()
    rows = list(conn.cursor().execute("select * from vw_occyymm where yymm>=strftime('%Y-%m',date('now','-2 months','start of month')) order by yymm, case when site='ridgefield' then 1 when site='wilton' then 2 when site='westport' then 3 when site='darien' then 4 when site='texas' then 5 when site='westport2' then 6 when site='darien2' then 7 else site end;").fetchall())
    #rows = curs.fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Month</th><th>Studio</th><th>Classes</th><th>Sold</th><th>Avail</th><th>Avg/Day</th><th>Avg/Cls</th><th>Occ%</th></tr>")
    for i, row in enumerate(rows):
        if i > 0 and rows[i][0] != rows[i-1][0]:
            io.write("<tr><td colspan='8' bgcolor='#aaaaaa'/></tr>")
        row = tuple([x or 0 for x in row])# handle None
        #print repr(row)
        io.write("<tr><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%.1f</td><td align='right'>%.1f</td><td align='right'>%.1f%%</td></tr>" % row)
    io.write("</table>")
    return io.getvalue()    
    
def get_history_by_instr():
    io = StringIO.StringIO()
    #curs = conn.cursor()
    rows = list(conn.cursor().execute("select * from vw_occyymmbyinstr where yymm>=strftime('%Y-%m',date('now','-1 months','start of month')) order by yymm, case when site='ridgefield' then 1 when site='wilton' then 2 when site='westport' then 3 when site='darien' then 4 when site='texas' then 5 when site='westport2' then 6 when site='darien2' then 7 else site end, instrex;").fetchall())
    #rows = curs.fetchall()
    io.write("<table border='1' cellpadding='1' cellspacing='1' bordercolor='#aaaaaa'>")
    io.write("<tr><th>Month</th><th>Studio</th><th>Instr</th><th>Classes</th><th>Sold</th><th>Avail</th><th>Avg/Cls</th><th>Occ%</th></tr>")
    for i, row in enumerate(rows):
        if i > 0 and rows[i][1] != rows[i-1][1]:
            io.write("<tr><td colspan='8' bgcolor='#aaaaaa'/></tr>")	
        io.write("<tr><td>%s</td><td>%s</td><td>%s</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%.1f</td><td align='right'>%.1f%%</td></tr>" % row)
    io.write("</table>")
    return io.getvalue()      

def send_report(report, subj):
    envelope = Envelope(
        from_addr=(u'joyride.robot@gmail.com', u'JoyRide Robot'),
        to_addr=['kevin.manley@gmail.com', 
                 'amylunapal@gmail.com', 
                      ],
        subject=subj,
        html_body=report
    )

    # Send the envelope using an ad-hoc connection...
    envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
              tls=True, port=587)

def main():
    io = StringIO.StringIO()
    io.write("<html><body>")
    io.write("Figures are approx 2% lower than actual since enrollments after start time aren't counted<br/>")
    io.write("<h4>Today</h4>")
    io.write(get_table(TODAY))
    io.write("<h4>Tomorrow</h4>")
    io.write(get_table(TOMORROW))
    io.write("<h4>Historical Summary by Studio</h4>")
    io.write(get_history_by_studio())
    io.write("<h4>Historical Summary by Instructor</h4>")
    io.write(get_history_by_instr())
    io.write("</body></html>")
    if dryRun:
        filename = "/tmp/test.html"
        print "dryRun: wrote %s" % filename
        with open(filename, "wb") as fp: 
            fp.write(io.getvalue())    
    else:
        send_report(io.getvalue(), 'Occupancy report %s - %s' % (str(TODAY), str(TOMORROW)))
        
    

if __name__ == "__main__":
    main()
