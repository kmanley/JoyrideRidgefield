import fetch_csv
import import_customers
import import_sales
import import_attendance

def main():
	fetch_csv.main()
	import_customers.main("customers.csv")
	import_sales.main("sales.csv")
	import_attendance.main("attendance.csv")

if __name__ == "__main__":
	main()
