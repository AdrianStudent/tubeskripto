from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from stegano import lsb
from PIL import Image
import numpy as np

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
    # Fungsi BPCS steganografi warna
    def hide_data(image, data):
        # Pisahkan gambar ke dalam komponen warna RGB
        red, green, blue = image.split()
        
        # Konversi komponen warna ke dalam array numpy
        red_np = np.array(red)
        green_np = np.array(green)
        blue_np = np.array(blue)
        
        # Pisahkan komponen warna ke dalam bit-plane
        red_bit_planes = [(red_np & (1 << i)) >> i for i in range(8)]
        green_bit_planes = [(green_np & (1 << i)) >> i for i in range(8)]
        blue_bit_planes = [(blue_np & (1 << i)) >> i for i in range(8)]
        
        # Ubah data ke dalam format biner
        data_bits = [int(bit) for bit in ''.join(format(byte, '08b') for byte in data)]
        
        # Cari bit-plane dengan kompleksitas tinggi untuk masing-masing komponen warna
        def calculate_complexity(bit_plane):
            height, width = bit_plane.shape
            complexity = 0
            # Hitung perubahan bit (dari 0 ke 1 atau 1 ke 0) dalam bit-plane
            for i in range(height):
                for j in range(width - 1):
                    complexity += abs(bit_plane[i, j] - bit_plane[i, j + 1])
            for j in range(width):
                for i in range(height - 1):
                    complexity += abs(bit_plane[i, j] - bit_plane[i + 1, j])
            return complexity / (height * width)
        
        def embed_data_in_bit_plane(bit_planes, data_bits):
            for i in range(7, -1, -1):
                complexity = calculate_complexity(bit_planes[i])
                if complexity > 0.3:  # Tetapkan batas kompleksitas untuk embed
                    index = 0
                    for r in range(bit_planes[i].shape[0]):
                        for c in range(bit_planes[i].shape[1]):
                            if index < len(data_bits):
                                bit_planes[i][r, c] = data_bits[index]
                                index += 1
                    return bit_planes
        
        # Embed data ke dalam bit-plane dengan kompleksitas tinggi
        red_bit_planes = embed_data_in_bit_plane(red_bit_planes, data_bits)
        green_bit_planes = embed_data_in_bit_plane(green_bit_planes, data_bits)
        blue_bit_planes = embed_data_in_bit_plane(blue_bit_planes, data_bits)
        
        # Rekonstruksi gambar dengan bit-plane yang dimodifikasi
        red = sum((plane << i) for i, plane in enumerate(red_bit_planes))
        green = sum((plane << i) for i, plane in enumerate(green_bit_planes))
        blue = sum((plane << i) for i, plane in enumerate(blue_bit_planes))
        
        # Gabungkan kembali gambar yang telah dimodifikasi
        new_image = Image.merge('RGB', (Image.fromarray(red), Image.fromarray(green), Image.fromarray(blue)))
        return new_image
    
    # Baca gambar
    image = Image.open(IMAGE_FILE)
    
    # Pesan rahasia yang akan disisipkan
    secret_message = "This is a secret message"
    secret_data = secret_message.encode()  # Ubah pesan menjadi biner
    
    # Sembunyikan data menggunakan BPCS steganografi warna
    steg_image = hide_data(image, secret_data)
    
    # Simpan gambar yang telah dimodifikasi
    steg_image.save(STEALTH_IMAGE_FILE)

# Main function
if __name__ == '__main__':
    generate_key_pair()
    sign_image()
    verify_signature()
    steganograph_image()
