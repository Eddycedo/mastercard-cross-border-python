from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from jose import jwe
from jose.exceptions import JOSEError
import logging

CLIENT_PASSCODE = "REPLACE WITH THE DECRYPTION KEY PASSCODE YOU CREATE WHILE CREATING THE DECRYPTION CERTIFICATE"
CLIENT_CERT_KEY = "REPLACE WITH CERTIFICATE KEY"

class EncryptionUtils:
    def __init__(self):
        self.cert_file_path = "REPLACE WITH ENCRYPTION CERTICATE KEY"
        self.pkcs12_file_path = "REPLACE WITH THE DECRYPTION CERTIFICATE YOU CREATED"

    def _read_pub_key_from_cert(self):
        with open(self.cert_file_path, "rb") as certificate:
            cert = certificate.read()
        cert_obj = x509.load_pem_x509_certificate(cert)
        public_key_obj = cert_obj.public_key()
        public_pem = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return public_pem.decode("utf-8")

    def _read_priv_key_from_pkcs12(self):
        with open(self.pkcs12_file_path, "rb") as pkfile:
            (private_key, _, _) = pkcs12.load_key_and_certificates(
                pkfile.read(), CLIENT_PASSCODE.encode()
            )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return private_pem.decode("utf-8")

    def jweEncryption(self, data):
        try:
            encrypted_data = jwe.encrypt(
                plaintext=data,
                key=self._read_pub_key_from_cert(),
                encryption="A256GCM",
                algorithm="RSA-OAEP-256",
                cty="application/json",
                kid=CLIENT_CERT_KEY,
            )
            return encrypted_data.decode("utf-8")
        except JOSEError as e:
            logging.error(f"Encryption failed: {e}")
            return None

    def jweDecrypt(self, cipher):
        try:
            private_key = self._read_priv_key_from_pkcs12()
            decrypted_data = jwe.decrypt(cipher, key=private_key)
            return decrypted_data.decode("utf-8")
        except JOSEError as e:
            logging.error(f"Decryption failed: {e}")
            return None
