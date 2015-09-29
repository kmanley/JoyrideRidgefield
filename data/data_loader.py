import fetch_csv
import import_customers
import import_sales
import import_attendance
import import_series
import sys

if len(sys.argv) < 2:
	print "usage: data_loader <site>"
	sys.exit(1)
site = sys.argv[1]

def main():
	fetch_csv.main(site)
	import_series.main("openseries-%s.csv" % site, site)
	import_customers.main("customers-%s.csv" % site, site)
	import_sales.main("sales-%s.csv" % site, site)
	import_attendance.main("attendance-%s.csv" % site, site)

if __name__ == "__main__":
	main()
