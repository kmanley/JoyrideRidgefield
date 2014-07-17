# Zingfit sucks!
import sys
import sqlite3
import csv

def main(csvfile):
	#print csvfile
	conn = sqlite3.connect("joyridge.dat")
	curs = conn.cursor()
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
			print repr(cols), "has %d cols" % len(cols)
			return
			sys.exit(2)
		cols = [unicode(col[1:-1] if col.startswith('"') else col, encoding="latin-1") for col in cols]
		print cols
		curs.execute("insert into sale (dt,custid,pmtype,total,item,typ,firstname,lastname,studio) values (?,?,?,?,?,?,?,?,?)",
	             tuple(cols))
	conn.commit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: import_sales.py <csvfile>"
        sys.exit(1)
    main(sys.argv[1])