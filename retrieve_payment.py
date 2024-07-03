import json
import requests
from config import BASE_URL, SECRET_FILE, CONSUMER_KEY, PASS_CODE
from encryption_utils import EncryptionUtils
from oauth1.authenticationutils import load_signing_key
from oauth1.oauth import OAuth
from http import HTTPMethod
import logging

class PaymentTransactionAPI:
    def __init__(self):
        pass

    def build_url(self, transaction_reference):
        return f"{BASE_URL}/send/v1/partners/SANDBOX_1234567/crossborder?ref={transaction_reference}"

    def authenticate(self, url, http_method):
        try:
            signing_key = load_signing_key(SECRET_FILE, PASS_CODE)
            auth_header = OAuth.get_authorization_header(url, http_method.name, "", CONSUMER_KEY, signing_key)
            return auth_header
        except Exception as e:
            logging.error(f"Error in authenticate: {e}")
            raise

    def retrieve_payment_transaction(self, transaction_reference):
        url = self.build_url(transaction_reference)
        logging.info(f"URL: {url}")
        oAuth_string = self.authenticate(url, HTTPMethod.GET)
        logging.info(f"OAuth Header: {oAuth_string}")

        headers = {
            "accept": "application/json",
            "authorization": oAuth_string,
        }

        logging.info(f"Request Headers: {headers}")

        response = requests.get(url, headers=headers)
        logging.info(f"Response Status Code: {response.status_code}")
        logging.info(f"Response Content: {response.content}")

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON response: {e}")
                return {"error": "Failed to parse JSON response"}
        else:
            logging.error(f"Retrieve payment transaction request failed with status code: {response.status_code}")
            return {"error": f"Retrieve payment transaction request failed with status code: {response.status_code}"}
