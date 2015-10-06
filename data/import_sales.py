# Zingfit sucks!
import sys
import sqlite3
import csv
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

def main(csvfile, site):
	assert site in csvfile # sanity check
	#print csvfile
	
	mindate = "9999-99-99 99:99:99.9"
	maxdate = "0000-00-00 00:00:00.0"
	lines = [x.strip() for x in open(csvfile, "rb").read().split("\r")]
	for i, line in enumerate(lines):
		if i==0:
			continue # skip header
		dt = line[:21]
		if dt < mindate:
			mindate = dt
		if dt > maxdate:
			maxdate = dt
		
	log.info( "importing sales from %s to %s" % (mindate, maxdate))
	
	conn = sqlite3.connect("joyride-%s.dat" % site)
	curs = conn.cursor()
	curs.execute("delete from sale where dt>='%s' and dt<='%s';" % (mindate, maxdate))
    # 0x0d line terminators - I told you zingfit sucks! 
	lines = [x.strip() for x in open(csvfile, "rb").read().split("\r")]
	#with open(csvfile, "ru") as fp:
	#	reader = csv.reader(fp, delimiter=',', quotechar='"', lineterminator='\r')
	for i, line in enumerate(lines):
		if i==0: continue
		#cols = line.split(",")
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
		if len(cols) != 9:
			log.error( repr(cols), "has %d cols" % len(cols))
			return
			sys.exit(2)
		cols = [unicode(col[1:-1] if col.startswith('"') else col, encoding="latin-1") for col in cols]
		#print cols
		curs.execute("insert into sale (dt,custid,pmtype,total,item,typ,firstname,lastname,studio) values (?,?,?,?,?,?,?,?,?)",
	             tuple(cols))
	conn.commit()
	log.info( "loaded %d sales" % i)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: import_sales.py <csvfile> <site>"
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
