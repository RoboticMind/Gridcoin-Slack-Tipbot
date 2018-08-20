#The author of this code Delta
import hashlib
from random import SystemRandom

def newpassword(rawpass):
	hasher = hashlib.sha512()
	binsalt = SystemRandom().getrandbits(512)
	salt = hex(binsalt)
	hasher.update((str(rawpass) + bin(binsalt)).encode())
	hashedpass = hasher.hexdigest()
	return hashedpass, salt #both are hexadecimal strings

def checkpassword(rawpass, hashedpass, salt):
	hasher = hashlib.sha512()
	hasher.update((str(rawpass) + bin(int(salt, 16))).encode())
	return hasher.hexdigest() == hashedpass