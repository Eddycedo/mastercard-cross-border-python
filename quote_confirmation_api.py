import json
import requests
from config import BASE_URL, SECRET_FILE, CONSUMER_KEY, PASS_CODE
from encryption_utils import EncryptionUtils
from oauth1.authenticationutils import load_signing_key
from oauth1.oauth import OAuth
from http import HTTPMethod
import logging
import time

class QuoteConfirmationAPI:
    def __init__(self):
        self.encryption_utils = EncryptionUtils()
        self.max_retries = 3
        self.retry_delay = 5  # seconds (increased to 5 seconds)

    def build_url(self):
        return BASE_URL + "/send/partners/SANDBOX_1234567/crossborder/quotes/confirmations"

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

    def confirm_quote(self, proposal_id, transaction_reference):
        payload = {
            "transactionReference": transaction_reference,
            "proposalId": proposal_id
        }

        request_str = json.dumps(payload)
        logging.info(f"Request Payload: {request_str}")
        request_body = self.get_encrypted_request_body(request_str)
        logging.info(f"Encrypted Request Payload: {request_body}")
        url = self.build_url()
        logging.info(f"URL: {url}")

        for attempt in range(self.max_retries):
            # Generate new OAuth header for each attempt
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

            try:
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
                    if response.status_code == 500 and attempt < self.max_retries - 1:
                        logging.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    elif response.status_code == 425 and attempt < self.max_retries - 1:
                        logging.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        return {"error": "Request failed with status code: " + str(response.status_code)}
            except Exception as e:
                logging.error(f"Exception during request: {e}")
                return {"error": f"Exception during request: {e}"}

