# Import necessary libraries
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from stegano import lsb

# Set constants
IMAGE_FILE = 'helicopter.jpg'  # Input image file
PRIVATE_KEY_FILE = 'private_key.pem'  # Private key file
PUBLIC_KEY_FILE = 'public_key.pem'  # Public key file
SIGNATURE_FILE = 'signature1.txt'  # Signature file
STEALTH_IMAGE_FILE = 'steg_image.jpg'  # Steganographed image file

# Generate DSA key pair
def generate_key_pair():
    key = DSA.generate(2048)
    print("Key object:", key)
    with open(PUBLIC_KEY_FILE, 'wb') as f:
        f.write(key.publickey().export_key())
    with open(PRIVATE_KEY_FILE, 'wb') as f:
        f.write(key.export_key("PEM", True))

# Sign image using DSA and SHA256
def sign_image():
    with open(IMAGE_FILE, 'rb') as f:
        image_data = f.read()
    hash_object = SHA256.new(image_data)
    print("Importing private key for sign")
    with open(PRIVATE_KEY_FILE, 'r') as f:
        key = DSA.import_key(f.read())
    signer = DSS.new(key, 'fips-186-3')
    signature = signer.sign(hash_object)
    print("Original message hash:", hash_object.hexdigest())
    print("Signature of original message hash:", signature)
    with open(SIGNATURE_FILE, 'wb') as f:
        f.write(signature)

# Verify signature using DSA and SHA256
def verify_signature():
    print("Importing public key for validating signature")
    with open(PUBLIC_KEY_FILE, 'r') as f:
        public_key = DSA.import_key(f.read())
    verifier = DSS.new(public_key, 'fips-186-3')
    with open(SIGNATURE_FILE, 'rb') as f:
        signature = f.read()
    with open(IMAGE_FILE, 'rb') as f:
        image_data = f.read()
    hash_object = SHA256.new(image_data)
    try:
        verifier.verify(hash_object, signature)
        print("The message is authentic.")
    except ValueError:
        print("The message is not authentic.")

# Perform BPCS steganography
def steganograph_image():
    secret_message = "This is a secret message"
    steg_image = lsb.hide(IMAGE_FILE, secret_message)
    steg_image.save(STEALTH_IMAGE_FILE)

# Main function
if __name__ == '__main__':
    generate_key_pair()
    sign_image()
    verify_signature()
    steganograph_image()