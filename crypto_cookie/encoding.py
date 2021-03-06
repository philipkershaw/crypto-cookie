"""Encoding module for crypto-cookie package
"""
__author__ = "@philipkershaw"
__date__ = "09/07/15"
__copyright__ = "(C) 2015 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from .encryption import Encryption
from .signature import Signature


class Encoder(object):
    '''Class to encrypt, sign and encode messages and handle the equivalent
    signature verification and decryption.  Uses symmetric key encryption
    (AES) and HMAC signature.
    '''
    DEFAULT_ENCODING = 'hex'
    DEFAULT_DELIMITER = "-"
    
    def __init__(self, encoding=DEFAULT_ENCODING, delimiter=DEFAULT_DELIMITER,
                 signature_kw=None, encryption_kw=None):
        '''Set encoding method'''
        self.encoding = encoding
        
        if signature_kw is None:
            signature_kw = {}

        self.signature = Signature(**signature_kw)
        
        if encryption_kw is None:
            encryption_kw = {}
            
        self.encryption = Encryption(**encryption_kw)
        
        self.delimiter = delimiter
        
    def encode_msg(self, msg, key):
        '''Encrypt message, encode it, sign it and concatenate encoded cipher
        text, encoded initialisation vector and signature
        '''
        cipher_text, iv = self.encryption.encrypt(msg, key)
        
        # Nb. encoded message is stripped to allow for base 64 encoding where
        # an in this case unwanted new line character is added.  Decoding is
        # not affected by this change
        encoded_cipher_text = cipher_text.encode(self.encoding).strip()
        encoded_iv = iv.encode(self.encoding).strip()
        
        digest = self.signature.sign(encoded_cipher_text, key)
        encoded_digest = digest.encode(self.encoding).strip()
        
        encoded_msg = self.delimiter.join([encoded_cipher_text, encoded_iv,
                                           encoded_digest])
        
        return encoded_msg
        
    def decode_msg(self, encoded_msg, key):
        '''Decode message, check signature and decrypt'''
        encoded_cipher_text, encoded_iv, encoded_digest = encoded_msg.split(
                                                                self.delimiter)
        
        cipher_text = encoded_cipher_text.decode(self.encoding)
        iv = encoded_iv.decode(self.encoding)
        digest = encoded_digest.decode(self.encoding)
        
        self.signature.verify_signature(encoded_cipher_text, digest, key)
        
        msg = self.encryption.decrypt(cipher_text, key, iv)
        
        return msg