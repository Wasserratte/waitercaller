import hashlib
import os
import base64


class PasswordHelper:

    def get_hash(self, plain):		#For registration a new user.
        return hashlib.sha512(plain).hexdigest() #sha512 hash for the
						 #final hash we will store.
    def get_salt(self):
        return base64.b64encode(os.urandom(20))	#os.urandom creates a cryptographically string. base64 encodes it.

    def validate_password(self, plain, salt, expected):
        return self.get_hash(plain + salt) == expected	#For the login process. Input passward and the salt we stored will
							#be hashed and compared to the stored hash(expected)
