import random
from PIL import Image

class Noise:
    @staticmethod
    def add_noise(image, noise_level, data_length):
        new_image = image.copy() # copy image and get width, height, and pixel data
        width, height = new_image.size
        pixels = new_image.load()

        noise_level_int = int(noise_level * 1000)  # convert to int, *1000 to ensure not a float
        skip_pixels = data_length * 8 * 3  # calc no. pixels to skip based on data length (*8 for bits, *3 for rgb)

        for _ in range(noise_level_int):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1) # generate random pixel coordinates
            pixel_index = y * width + x # pixel index used to skip pixels
            if pixel_index < skip_pixels: # skip pixels containing embedded data
                continue
            r, g, b = pixels[x, y] # get pixel's rgb
            noise = random.randint(-int(noise_level), int(noise_level))  # generate random noise
            pixels[x, y] = (Noise._clamp(r + noise), Noise._clamp(g + noise), Noise._clamp(b + noise))  # actually add noise

        return new_image

    @staticmethod
    def _clamp(value):
        return max(0, min(255, value))  # ensure value is within range [0, 255] (inclusive) (rgb)
