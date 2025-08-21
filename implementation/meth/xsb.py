class SignificantBit:
    @staticmethod
    def _transform_data_to_binary(data):
        return [format(byte, '08b') for byte in data] # convert data to binary

    @staticmethod
    def _manipulate_pixels(pixels, data, bit_position):
        bit_position = min(7, max(0, bit_position)) # ensure bit_position is within valid range (0-7)
        binary_data = SignificantBit._transform_data_to_binary(data) # convert data to binary
        data_length = len(binary_data)
        pixel_iterator = iter(pixels)
        for idx in range(data_length): # iterate over data
            pixel_block = []
            for _ in range(3):
                pixel_block.extend(next(pixel_iterator)[:3]) # collect 9 pixel values (3 RGB pixels)
            for bit_idx in range(8): # iterate over bits in byte
                bit_mask = (1 << bit_position)
                if binary_data[idx][bit_idx] == '0': # check if bit is 0
                    pixel_block[bit_idx] = pixel_block[bit_idx] & ~bit_mask # clear the specified bit
                else:
                    pixel_block[bit_idx] = pixel_block[bit_idx] | bit_mask # set the specified bit
            if idx == data_length - 1:
                pixel_block[8] = pixel_block[8] & ~(1 << bit_position) # end of data marker - clear the bit
            else:
                pixel_block[8] = pixel_block[8] | (1 << bit_position) # more data follows - set the bit
            yield tuple(pixel_block[0:3]) # return the pixel groups
            yield tuple(pixel_block[3:6])
            yield tuple(pixel_block[6:9])

    @staticmethod
    def embed(image, data, bit_depth=8, bit_position=0): # embed data in image at specified bit position
        if not data:
            raise ValueError('Data is empty')            
        bit_position = min(7, max(0, bit_position)) # ensure bit_position is within valid range (0-7)
        new_image = image.copy()
        width = new_image.size[0]
        x, y = 0, 0
        for pixel in SignificantBit._manipulate_pixels(new_image.getdata(), data, bit_position): # iterate over pixels and modify them
            new_image.putpixel((x, y), pixel) # set the pixel value
            x += 1
            if x >= width:
                x = 0 # reset x if at end of row
                y += 1
        return new_image

    @staticmethod
    def extract(image, bit_depth=8, bit_position=0): # extract data from image at specified bit position
        bit_position = min(7, max(0, bit_position)) # ensure bit_position is within valid range (0-7)
        extracted_data = ''
        pixel_iterator = iter(image.getdata())
        bit_mask = 1 << bit_position # create bit mask (used to extract specific bit)
        char_counter = 0
        try:
            while True:
                pixels_block = []
                try:
                    for _ in range(3): # iterate over 3 pixels
                        pixel = next(pixel_iterator) # get the pixel value
                        pixels_block.extend(pixel[:3]) # collect 9 pixel values
                except StopIteration:
                    break
                binary_string = ''
                for i in range(8): # iterate over bits in byte
                    bit_value = '0' if (pixels_block[i] & bit_mask) == 0 else '1'
                    binary_string += bit_value # extract bits from first 8 pixels
                try:
                    int_value = int(binary_string, 2) # convert binary to integer
                    char = chr(int_value) # convert binary to character
                    extracted_data += char # add character to extracted data
                    char_counter += 1
                except ValueError:
                    break
                end_marker_bit = (pixels_block[8] & bit_mask) == 0 # check if this is the end of data
                if end_marker_bit:
                    break
                if char_counter > 10000: # safety check to prevent infinite loops
                    break
        except Exception: # shouldn't happen, but just in case
            pass
            
        return extracted_data # return the extracted data
