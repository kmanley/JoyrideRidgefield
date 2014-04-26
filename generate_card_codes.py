import random, time
random.seed(time.time())

def main():
    # No easily misread chars; i, o, 1, 0
    codechars = list("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
    pinchars = list("0123456789")
    codes = set()
    while len(codes) < 250:
        random.shuffle(codechars)
        codes.add("".join(codechars[:6]))
    for i, code in enumerate(codes):
        random.shuffle(pinchars)
        pin = "".join(pinchars[:3])
        print "Code: %s  PIN: %s" % (code, pin)
    


if __name__ == "__main__":
    main()
