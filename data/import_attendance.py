# Zingfit sucks!
import sys
import sqlite3
import csv

def main(csvfile, site):
	assert site in csvfile # sanity check
	#print csvfile
	
	conn = sqlite3.connect("joyride-%s.dat" % site)
	curs = conn.cursor()
	curs.execute("begin transaction;")
	#minident = 9999999999L
	#maxident = 0L
	lines = [x.strip() for x in open(csvfile, "rb").read().split("\r") if x]
	#lastident = 0L
	for i, line in enumerate(lines):
		#print line
		#print
		if i==0:
			continue # skip header
		try:
			ident = long(line.split(",")[0][1:-1])
		except Exception:
			print "bad line %d: %s" % (i, repr(line))
			sys.exit(1)
		#if ident < lastident:
		#	raise Exception("file is not sorted!")
		#lastident = ident
		#if ident < minident:
		#	minident = ident
		#if ident > maxident:
		#	maxident = ident
		curs.execute("delete from attend where id=%s" % ident)
	
	conn.commit()	
	#print "importing attendance from %s to %s" % (minident, maxident)	
	#sys.exit(0)
	
	#conn = sqlite3.connect("joyride-%s.dat" % site)
	#curs = conn.cursor()
	#curs.execute("delete from attend where id>='%s' and id<='%s';" % (minident, maxident))
    # 0x0d line terminators - I told you zingfit sucks! 
	lines = [x.strip() for x in open(csvfile, "rb").read().split("\r") if x]
	rows = []
	# first pass, build up rows
	for i, line in enumerate(lines):
		cols = []
		j = 0
		inquote = False
		for k in range(len(line)):
			if line[k] == '"':
				inquote = not inquote
			elif line[k] == ",":
				if inquote:
					pass
				else:
					cols.append(line[j:k])
					j = k+1
		cols.append(line[j:k+1])
		if len(cols) != 15:
			print repr(cols), "has %d cols (line %d)" % (len(cols), i)
			return
			sys.exit(2)
		cols = [unicode(col[1:-1] if col.startswith('"') else col, encoding="latin-1") for col in cols]
		#custid = cols[1]
		#status = cols[5]
		rows.append(cols)

	header = rows[0]
	idx_custid = header.index("CUSTOMERID")
	idx_status = header.index("STATUS")
	idx_classdate = header.index("CLASSDATE")
	idx_datein = header.index("DATEIN")
	#print idx_classdate, idx_datein
	#import sys
	#sys.exit(0)
	# eliminate header
	rows = rows[1:]
	rows.sort(lambda lhs, rhs: cmp(lhs[idx_classdate], rhs[idx_classdate]) or cmp(lhs[idx_datein], rhs[idx_datein]))
	#for row in rows:
	#	print row[0], row[1], row[2], row[3], row[7], row[10]
	#import sys
	#sys.exit(0)
		
		
	enrolled = {} # custid -> enroll count
	lastcountrows = conn.cursor().execute("select custid, max(num) from attend group by custid;").fetchall()
	for custid, custcount in lastcountrows:
		enrolled[custid] = int(custcount)
		
	totenrolled = int(conn.cursor().execute("select coalesce(max(totnum),0) from attend;").fetchall()[0][0]) # total enrolled across all customers

	#print enrolled
	#print enrolled[7453]
	#print totenrolled
	#sys.exit(0)
		
	for i, row in enumerate(rows):
		custid = int(row[idx_custid])
		status = row[idx_status]
		#print custid, status
		enrolled.setdefault(custid, 0)
		if status == "Enrolled":
			enrolled[custid] = enrolled[custid] + 1
			totenrolled += 1
			
		#print cols
		if i>0 and i % 1000 == 0:
			print "%d rows..." % i
		curs.execute("insert into attend values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
	             tuple(row)+(enrolled[custid],totenrolled))
	conn.commit()
	print "loaded %d attendance rows" % i

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: import_attendance.py <csvfile> <site>"
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
