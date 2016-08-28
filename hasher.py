import hashlib
import hmac
import random
import string


salt = '7uycYyynRb'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(salt, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def make_salt(length=5):
    return ''.join(random.SystemRandom().choice(string.letters) for x in range(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (salt, h)


def valid_pw(name, pw, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, pw, salt)
