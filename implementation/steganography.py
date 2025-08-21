import json
import base64
import logging
from PIL import Image
from meth.xsb import SignificantBit
from meth.pvd import PVDAlgorithm
from enc.aes import AESAlgorithm
from enc.noise import Noise

logging.basicConfig(filename='steganography.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # basic action logging config

class Steganography:
    def __init__(self, config):
        self._config = config  
        self._aes = None  
        self._iv = None
        self._initialize_encryption()
        logging.info(f"Initialised Steganography with config: {self._config}")

    def _initialize_encryption(self):
        if self._config['encryption'] == 'AES':
            if 'key' in self._config and 'iv' in self._config: # encode key and iv if they exist
                self._aes = AESAlgorithm(self._config['key'].encode())
                self._iv = self._config['iv'].encode()
            else:
                raise KeyError("AES encryption selected but no key or IV provided in the configuration.")

    @staticmethod
    def load_config(file_path): # utility function to load config from file
        with open(file_path, 'r') as file:
            config = json.load(file)
        logging.info(f"Loaded config from: {file_path}")
        return config

    def embed_text(self, image_path, text):
        logging.info(f"Embedding text into image: {image_path}")
        image = Image.open(image_path)
        if image.mode != 'RGB': # convert to RGB if not already
            image = image.convert('RGB')
        data = self._apply_encryption(text.encode()) # encode text if encryption is enabled
        logging.info(f"Encrypted data length: {len(data)}")
        data_with_end_marker = data + b'###END###' # add end marker
        image = self._apply_algorithm(image, data_with_end_marker)
        image = Noise.add_noise(image, self._config['noise_level'], len(data_with_end_marker)) # add noise
        return image

    def save_image(self, image, save_path): # utility function to save image
        image.save(save_path)
        logging.info(f"Saved stego image to: {save_path}")

    def decode_text(self, image_path):
        logging.info(f"Decoding text from image: {image_path}")
        image = Image.open(image_path)
        data = self._extract_data(image)
        if self._config['encryption'] == 'None':
            return data.replace('###END###', '')
        data = data.replace('###END###', '')
        decrypted_data = self._apply_decryption(data.encode('latin1')) # decode if encryption enabled, latin1 encoding (for aes mostly)
        logging.info(f"Decrypted data length: {len(decrypted_data)}")
        return decrypted_data.decode()

    def _extract_data(self, image):
        if self._config['algorithm'] == 'X Significant Bit':
            bit_position = self._config.get('bit_position', 8) # get bit position if it exists
            return SignificantBit.extract(image, bit_position=bit_position) # extract with xsb
        elif self._config['algorithm'] == 'Pixel Value Differencing':
            return PVDAlgorithm.extract(image) # extract with pvd
        else:
            raise ValueError(f"Unsupported algorithm: {self._config['algorithm']}")

    def _apply_algorithm(self, image, data):
        logging.info(f"Applying algorithm: {self._config['algorithm']}")
        if self._config['algorithm'] == 'X Significant Bit':
            bit_position = self._config.get('bit_position', 8) # get bit position if it exists
            return SignificantBit.embed(image, data, bit_position=bit_position) # embed with xsb
        if self._config['algorithm'] == 'Pixel Value Differencing':
            return PVDAlgorithm.embed(image, data) # embed with pvd
        return image

    def _apply_encryption(self, data):
        logging.info(f"Applying encryption: {self._config['encryption']}")
        if self._config['encryption'] == 'Base64':
            return base64.b64encode(data) # encrypt data with base64
        elif self._config['encryption'] == 'AES':
            return self._aes.encrypt_cbc_mode(data, self._iv) # encrypt data with aes
        elif self._config['encryption'] == 'None':
            return data # return as is
        return data
    
    def _apply_decryption(self, data):
        logging.info(f"Applying decryption: {self._config['encryption']}")
        if self._config['encryption'] == 'Base64':
            missing_padding = len(data) % 4 # base64 requires data length to be multiple of 4
            if missing_padding:
                data += b'=' * (4 - missing_padding) # pads with '=' to meet requirement
            return base64.b64decode(data)
        elif self._config['encryption'] == 'AES':
            return self._aes.decrypt_cbc_mode(data, self._iv) # decrypt with aes
        elif self._config['encryption'] == 'None':
            return data # return as is
        return data