import fetch_csv
import import_customers
import import_sales
import import_attendance
import import_series

def main():
	fetch_csv.main()
	import_series.main("openseries.csv")
	import_customers.main("customers.csv")
	import_sales.main("sales.csv")
	import_attendance.main("attendance.csv")

if __name__ == "__main__":
	main()
