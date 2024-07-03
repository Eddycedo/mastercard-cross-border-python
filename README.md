# Mastercard Cross-Border APIs (Python)

This repository provides a Python implementation for Mastercard Cross-Border APIs. While Mastercard provides a Java implementation, this repository aims to simplify things by providing a Python alternative. The APIs covered in this repository are:

- Quote
- Quote Confirmation
- Payment
- Retrieve Payment
- Cancel Payment

## Getting Started

### Prerequisites

1. **Create a Mastercard Account:**
   - Sign up at the [Mastercard Developer Portal](https://developer.mastercard.com/).

2. **Create a Project:**
   - Once logged in, create a new project to access the necessary credentials.

3. **Obtain Credentials:**
   - After creating the project, you will have access to the following:
     - Consumer Key
     - Encryption Key
     - Decryption Key

4. **Download Certificates:**
   - Download the P12 file. This file contains your private key and certificate.
   - Download the encryption certificate. All communication with Mastercard needs to be encrypted.

5. **Add Decryption Keys:**
   - Add new keys for decryption of Mastercard messages.
   - Download the decryption certificate.

### Setup

1. **Add Certificates to Code Path:**
   - Place the P12 file, encryption certificate, and decryption certificate in the appropriate directory in your project.

### Usage

To use the APIs, follow the instructions provided in the individual scripts for each API. The following APIs are covered:

- **Quote:** Retrieve a quote for a cross-border payment.
- **Quote Confirmation:** Confirm a quote for a cross-border payment.
- **Payment:** Initiate a cross-border payment.
- **Retrieve Payment:** Retrieve details of a previously initiated payment.
- **Cancel Payment:** Cancel a previously initiated payment.

## Contributing

Feel free to fork this repository, make modifications, and submit pull requests. Contributions are welcome!



## Acknowledgments

- Thanks to Mastercard for providing comprehensive documentation and API support.

