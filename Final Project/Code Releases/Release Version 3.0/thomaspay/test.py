import hashlib

dk = hashlib.pbkdf2_hmac('SHA256', b'password', b'salt', 100000)
encoded_dk = dk.encode('base64')
print(dk)
print(encoded_dk)
print(dk == encoded_dk)

p = hashlib.sha256(b'Hello')
print(dk, p)
print(dk == p)

