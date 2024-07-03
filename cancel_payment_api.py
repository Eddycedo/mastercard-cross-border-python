# cancel_payment_api.py

import json
import requests
from config import BASE_URL, SECRET_FILE, CONSUMER_KEY, PASS_CODE
from encryption_utils import EncryptionUtils
from oauth1.authenticationutils import load_signing_key
from oauth1.oauth import OAuth
from http import HTTPMethod
import logging

class CancelPaymentAPI:
    def __init__(self):
        self.encryption_utils = EncryptionUtils()

    def build_url(self, payment_id):
        return f"{BASE_URL}/send/v1/partners/SANDBOX_1234567/crossborder/{payment_id}/cancel"

    def authenticate(self, url, http_method, request_str):
        try:
            signing_key = load_signing_key(SECRET_FILE, PASS_CODE)
            auth_header = OAuth.get_authorization_header(url, http_method.name, request_str, CONSUMER_KEY, signing_key)
            return auth_header
        except Exception as e:
            logging.error(f"Error in authenticate: {e}")
            raise

    def get_encrypted_request_body(self, request_str):
        try:
            encrypted_str = self.encryption_utils.jweEncryption(request_str)
            if not encrypted_str:
                raise ValueError("Encryption failed, resulting in an empty string.")
            logging.info(f"Encrypted string: {encrypted_str}")
            return '{"encrypted_payload":{"data":"' + encrypted_str + '"}}'
        except Exception as e:
            logging.error(f"Error in get_encrypted_request_body: {e}")
            raise

    def cancel_payment(self, payment_id):
        payload = {
            "cancelpaymentrequest": ""
        }

        request_str = json.dumps(payload)
        logging.info(f"Request Payload: {request_str}")
        request_body = self.get_encrypted_request_body(request_str)
        logging.info(f"Encrypted Request Payload: {request_body}")
        url = self.build_url(payment_id)
        logging.info(f"URL: {url}")
        oAuth_string = self.authenticate(url, HTTPMethod.POST, request_body)
        logging.info(f"OAuth Header: {oAuth_string}")

        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "x-mc-routing": "nextgen-apigw",
            "x-encrypted": "true",
            "authorization": oAuth_string,
        }

        logging.info(f"Request Headers: {headers}")

        response = requests.post(url, data=request_body, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")
        logging.info(f"Response Content: {response.content}")

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                return {"error": "Failed to parse JSON response"}
        else:
            logging.error(f"Request failed with status code: {response.status_code}")
            return {"error": "Request failed with status code: " + str(response.status_code)}
