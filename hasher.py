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


def make_img_url_hash(val):
    """ This function slices the end of the img url, which is a unique key """
    img_url_key = val[-10:-2]
    return hmac.new(salt, img_url_key).hexdigest()


def check_img_url_hash(img_url, secure_val):
    """ This function checks the img_url_hash and returns empty string or
        an error message """
    if secure_val == make_img_url_hash(img_url):
        return ''
    else:
        return '<div style="font-size:10em;">GET AWAY FROM ME, SCARY HACKER!</div>'


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
