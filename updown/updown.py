import os
import time
import datetime
from envelopes import Envelope, GMailSMTP
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("updown")
log.setLevel(logging.INFO)

secrets = open(".mailreport-secret").read().strip().split(";")

def send_mail(subj, body=""):
	recips = ['kevin@joyrideridgefield.com',]
	log.info("sending mail to %s" % repr(recips))
	envelope = Envelope(
	    from_addr=(u'joyride.robot@gmail.com', u'JoyRide Robot'),
	    to_addr=recips,
	    subject=subj,
	    text_body=body
	)

	# Send the envelope using an ad-hoc connection...
	envelope.send('smtp.googlemail.com', login=secrets[0], password=secrets[1],
					tls=True, port=587)

def main():
	log.info("starting...")
	lastdown = None # so we always get a mail on startup
	while True:
		# quit at 1am, cron will restart at 5a
		if datetime.datetime.now().hour == 1:
			log.info("exiting...")
			return
		consumer = os.system("curl -L --silent --connect-timeout 5 --max-time 10 http://joyrideridgefield.com/ > /dev/null")
		admin = os.system("curl -L --silent --connect-timeout 5 --max-time 10 http://joyrideridgefield.com/admin > /dev/null")
		if consumer or admin:
			down = True
			fn = log.warning
		else:
			down = False
			fn = log.info
		msg = "consumer site %s, admin site %s" % ("UP" if consumer==0 else "DOWN", "UP" if admin==0 else "DOWN")
		fn(msg)
		# TODO: flap prevention
		if down != lastdown:
			send_mail(msg)
		lastdown = down
		time.sleep(60)

if __name__ == "__main__":
	main()
