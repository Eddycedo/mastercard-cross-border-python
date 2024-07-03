import logging
from flask import Flask, request, jsonify
from quotes_api import QuotesAPI
from encryption_utils import EncryptionUtils
import json
from config import SECRET_FILE,PASS_CODE
from quote_confirmation_api import QuoteConfirmationAPI
from payment_api import PaymentAPI
from retrieve_payment import PaymentTransactionAPI
from cancel_payment_api import CancelPaymentAPI
# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

encryptUtil = EncryptionUtils()

@app.route('/quote', methods=['POST'])
def get_quote():
    quotes_api = QuotesAPI()
    response = quotes_api.make_request()
    logging.info(f"Received response: {response}")
    cipher = response.get("encrypted_payload", {}).get("data")
    if cipher and isinstance(cipher, str) and cipher.count('.') == 4:
        data = encryptUtil.jweDecrypt(cipher)
        logging.info(f"Decrypted data: {data}")
        print("Decrypted data tye is", type(data))
        return (data)
    else:
        logging.error("Invalid JWE token format!")
        return jsonify({"error": "Invalid JWE token format!"}), 400
    


@app.route('/quote/confirm', methods=['POST'])
def confirm_quote():
    print("Request received at /quote/confirm")

    # Call the get_quote function from app.py to retrieve the decrypted response
    decrypted_response_str = get_quote()

    # Parse the decrypted response JSON string
    try:
        decrypted_response = json.loads(decrypted_response_str)
    except json.JSONDecodeError as e:
        print(f"Failed to parse decrypted response: {e}")
        return jsonify({"error": "Failed to parse decrypted response"}), 400

    # Extract proposal_id and transaction_reference
    try:
        proposal_id = decrypted_response['quote']['proposals']['proposal'][0]['id']
        transaction_reference = decrypted_response['quote']['transaction_reference']
    except KeyError:
        print("Missing proposal_id or transaction_reference")
        return jsonify({"error": "Missing proposal_id or transaction_reference"}), 400

    # Make the confirmation request
    quote_confirmation_api = QuoteConfirmationAPI()
    confirmation_response = quote_confirmation_api.confirm_quote(proposal_id, transaction_reference)
    print("Confirmation Response:", confirmation_response)
    

    if 'error' in confirmation_response:
        return jsonify(confirmation_response), 400

    # Decrypt the response from the confirmation API
    decrypted_confirmation_response = encryptUtil.jweDecrypt(confirmation_response['encrypted_payload']['data'])
    print("Decrypted Confirmation Response:", decrypted_confirmation_response)

    return jsonify(json.loads(decrypted_confirmation_response))

@app.route('/quote/confirm/payment', methods=['POST'])
def make_payment():
    decrypted_response_str = get_quote()

    # Parse the decrypted response JSON string
    try:
        decrypted_response = json.loads(decrypted_response_str)
    except json.JSONDecodeError as e:
        print(f"Failed to parse decrypted response: {e}")
        return jsonify({"error": "Failed to parse decrypted response"}), 400
    
    # Extract proposal_id and transaction_reference
    try:
        proposal_id = decrypted_response['quote']['proposals']['proposal'][0]['id']
        transaction_reference = decrypted_response['quote']['transaction_reference']
    except KeyError:
        print("Missing proposal_id or transaction_reference")
        return jsonify({"error": "Missing proposal_id or transaction_reference"}), 400
    
    # Make the payment request
    payment_api = PaymentAPI()
    payment_response = payment_api.payment(proposal_id, transaction_reference)
    print("Payment Response:", payment_response)

    if 'error' in payment_response:
        return jsonify(payment_response), 400
    
    # Decrypt the response from the payment API
    decrypted_payment_response = encryptUtil.jweDecrypt(payment_response['encrypted_payload']['data'])
    print("Decrypted Payment Response:", decrypted_payment_response)

    return decrypted_payment_response  # Return the decrypted response as a string

@app.route('/payment/retrieve', methods=['GET'])
def retrieve_payment():
    # Assuming make_payment returns a JSON string as the response
    decrypted_response_str = make_payment()

    # Parse the decrypted response JSON string
    try:
        decrypted_response = json.loads(decrypted_response_str)
    except json.JSONDecodeError as e:
        print(f"Failed to parse decrypted response: {e}")
        return jsonify({"error": "Failed to parse decrypted response"}), 400
    
    # Extract transaction_reference
    try:
        transaction_reference = decrypted_response['payment']['transaction_reference']
    except KeyError:
        print("Missing transaction_reference")
        return jsonify({"error": "Missing transaction_reference"}), 400
    
    # Make the retrieve payment request
    retrieve_payment_api = PaymentTransactionAPI()
    retrieve_response = retrieve_payment_api.retrieve_payment_transaction(transaction_reference)
    print("Payment Response:", retrieve_response)
    return(retrieve_response)
    
    #if 'error' in retrieve_response:
       # return jsonify(retrieve_response), 400
    
    # Decrypt the response from the retrieve payment API
    #decrypted_payment_response = encryptUtil.jweDecrypt(retrieve_response)
    #print("Decrypted Retrieve Payment Response:", decrypted_payment_response)

    #return jsonify(json.loads(retrieve_response))

@app.route('/payment/cancel', methods=['POST'])
def cancel_payment():
    decrypted_response_str = make_payment()

    # Parse the decrypted response JSON string
    try:
        decrypted_response = json.loads(decrypted_response_str)
    except json.JSONDecodeError as e:
        print(f"Failed to parse decrypted response: {e}")
        return jsonify({"error": "Failed to parse decrypted response"}), 400
    
    # Extract payment_id

    try:
        payment_id=decrypted_response['payment']['id']
    except KeyError:
        print("Missing payment_id")
        return jsonify({"error": "Missing payment_id"}), 400
    
     # Make the retrieve payment request
    cancel_payment_api = CancelPaymentAPI()
    retrieve_response = cancel_payment_api.cancel_payment(payment_id)
    print("Payment Response:", retrieve_response)
    #return(retrieve_response)

    if 'error' in retrieve_response:
        return jsonify(retrieve_response), 400
    
    # Decrypt the response from the payment API
    decrypted_cancel_response = encryptUtil.jweDecrypt(retrieve_response['encrypted_payload']['data'])
    print("Decrypted Payment Response:", decrypted_cancel_response)

    return jsonify(json.loads(decrypted_cancel_response))  # Return the decrypted response as a string










if __name__ == '__main__':
    app.run(debug=True)
