import os
import time
import datetime
from envelopes import Envelope, GMailSMTP
today = datetime.date.today()
import logging

dryRun = False

if dryRun:
	logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
else:
	logging.basicConfig(filename="./logs/updown-%s.log" % str(today), format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")		
log = logging.getLogger("updown")
log.setLevel(logging.INFO)

secrets = open(".mailreport-secret").read().strip().split(";")

def send_mail(subj, body=""):
	recips = ['kevin@joyrideridgefield.com',]
	log.info("sending mail to %s: %s" % (repr(recips), subj))
	if dryRun:
		return
	envelope = Envelope(
		from_addr=(u'joyride.robot@gmail.com', u'JoyRide Robot'),
		to_addr=recips,
		subject=subj,
		text_body=body
	)

	# Send the envelope using an ad-hoc connection...
	envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
					tls=True, port=587)

#                *    u     d     u     d     u     d     d*    d     d*    u*    u     u
dummycheck = iter([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0]) #1, 1, 1, 0, 1, 1, 1, 1, 0, 0])
def check(url):
	if dryRun:
		return next(dummycheck)
	ret = os.system("curl -L --silent --connect-timeout 5 --max-time 10 %s > /dev/null" % url)
	return ret

def main():
	log.info("starting...")
	initialmail = False
	downcount = 0
	while True:
		needmail = False
		# quit at 1am, cron will restart at 5a
		if datetime.datetime.now().hour == 1:
			log.info("exiting...")
			return
		consumer = check("http://joyrideridgefield.com/")
		admin    = check("http://joyrideridgefield.com/admin")
		if consumer or admin:
			down = True
			fn = log.warning
		else:
			down = False
			fn = log.info
		# TODO: flap prevention
		if down:
			downcount += 1
			# if down for 2 mins in a row send email every 2 mins
			if downcount % 2 == 0:
				needmail = True
		else:
			if downcount >= 2:
				# we sent email about services DOWN, so notify about services UP
				needmail = True
			downcount = 0
		msg = "consumer site %s, admin site %s, downcount %d" % ("UP" if consumer==0 else "DOWN", "UP" if admin==0 else "DOWN", downcount)
		fn(msg)
		if needmail or not initialmail:
			send_mail(msg)
			initialmail = True
		lastdown = down
		time.sleep(1 if dryRun else 60)

if __name__ == "__main__":
	main()
