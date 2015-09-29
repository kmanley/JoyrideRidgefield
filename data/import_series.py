# Zingfit sucks!
import sys
import sqlite3
import csv

def main(csvfile, site):
	assert site in csvfile # sanity check
	#print csvfile
	conn = sqlite3.connect("joyride-%s.dat" % site)
	curs = conn.cursor()
	curs.execute("delete from openseries")
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
		if len(cols) != 12:
			print repr(cols), "has %d cols" % len(cols)
			return
			sys.exit(2)
		cols = [unicode(col[1:-1] if col.startswith('"') else col, encoding="latin-1") for col in cols]
		#print cols
		curs.execute("insert into openseries (emailaddress,firstname,lastname,series,cost,count,remaining,purchdt,expiredt,comped,lastclass,prefloc) values (?,?,?,?,?,?,?,?,?,?,?,?)",
	             tuple(cols))
	conn.commit()
	print "loaded %d open series" % i

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: import_series.py <csvfile> <site>"
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
