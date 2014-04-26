import sys
import csv
import datetime
today = datetime.date.today()

def run(filename, from_age, to_age):
    ctr = 0
    outfilename = "customers_age_%d_to_%d.txt" % (from_age, to_age)
    with open(outfilename, "w") as output:
        with open(filename) as fp:
            reader = csv.DictReader(fp)
            for line in reader:
                sbirthdate = line["birthdate"][:10].strip()
                if sbirthdate:
                    birthdate = datetime.date(int(sbirthdate[:4]), int(sbirthdate[5:7]), int(sbirthdate[-2:]))
                    emailaddress = line["emailaddress"]
                    years = (today - birthdate).days / 365. 
                    if from_age <= years < to_age:
                        ctr += 1
                        print emailaddress, birthdate, years
                        output.write(emailaddress + "\n")
    print "wrote %d emails to %s" % (ctr, outfilename)

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        from_age = int(sys.argv[2])
        to_age = int(sys.argv[3])
    except Exception:
        print "usage: %s <filename> <from_age> <to_age>" % sys.argv[0] 
        sys.exit(0)
    run(filename, from_age, to_age)
