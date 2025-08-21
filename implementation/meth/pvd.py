from PIL import Image
import numpy as np

class PVDAlgorithm:
    # range table defines pixel difference ranges and bits that can be stored:
    # smaller differences (smooth areas) store fewer bits to maintain image quality
    # larger differences (edge areas) can store more bits as changes are less noticeable
    RANGE_TABLE = ( 
        (0, 7),    # smooth regions: 3 bits - minimal visual impact
        (8, 15),   # slight texture: 3 bits - still maintains quality
        (16, 31),  # more texture: 4 bits - moderate capacity
        (32, 63),  # edges start: 5 bits - higher capacity
        (64, 127), # strong edges: 6 bits - even more data
        (128, 255) # dramatic changes: 7 bits - maximum capacity
    )
    BITS_PER_RANGE = (3, 3, 4, 5, 6, 7) # lookup table for quick bit capacity checks

    @staticmethod
    def _get_range_index(diff): # optimized range lookup - avoids binary search
        if diff <= 7: return 0
        elif diff <= 15: return 1
        elif diff <= 31: return 2
        elif diff <= 63: return 3
        elif diff <= 127: return 4
        return 5

    @staticmethod
    def embed(image, data): # embed data using PVD - modifies pixel pairs based on their difference
        if not data:
            raise ValueError('Data is empty')
        pixel_array = np.array(image) # convert to numpy array for faster operations
        binary_data = ''.join(format(byte, '08b') for byte in data + b'###END###') # add end marker for extraction
        height, width = pixel_array.shape[:2]
        data_index = 0 # tracks position in binary data string
        data_len = len(binary_data)
        
        for y in range(height):
            if data_index >= data_len: # all data embedded
                break
            for x in range(0, width - 1, 2): # process pixel pairs (p1,p2) in each row
                if data_index >= data_len:
                    break
                for c in range(3): # embed in each RGB channel
                    if data_index >= data_len:
                        break
                    # get pixel pair values and calculate their difference
                    p1 = int(pixel_array[y, x, c])
                    p2 = int(pixel_array[y, x + 1, c])
                    diff = abs(p2 - p1) # original difference determines embedding capacity
                    
                    # determine how many bits we can embed based on the difference
                    range_idx = PVDAlgorithm._get_range_index(diff)
                    num_bits = PVDAlgorithm.BITS_PER_RANGE[range_idx] # get capacity for this range
                    lower = PVDAlgorithm.RANGE_TABLE[range_idx][0] # lower bound of range
                    
                    # extract bits to embed and calculate new difference to achieve
                    to_embed = int(binary_data[data_index:data_index + num_bits], 2)
                    new_diff = lower + to_embed # target difference after embedding
                    
                    # adjust pixel values to achieve new difference while minimizing changes
                    if p1 <= p2: # maintain relative ordering of pixels
                        if new_diff > diff: # need to increase difference
                            p1_new = p1 # keep smaller pixel same
                            p2_new = p1 + new_diff # adjust larger pixel up
                        else: # need to decrease difference
                            p2_new = p2 # keep larger pixel same
                            p1_new = p2 - new_diff # adjust smaller pixel up
                    else: # p1 > p2 case
                        if new_diff > diff:
                            p2_new = p2 # keep smaller pixel same
                            p1_new = p2 + new_diff # adjust larger pixel up
                        else:
                            p1_new = p1 # keep larger pixel same
                            p2_new = p1 - new_diff # adjust smaller pixel down
                            
                    # clamp values to valid pixel range (0-255)
                    p1_new = max(0, min(255, p1_new))
                    p2_new = max(0, min(255, p2_new))
                    
                    # update pixel values and move to next bits
                    pixel_array[y, x, c] = p1_new
                    pixel_array[y, x + 1, c] = p2_new
                    data_index += num_bits
        return Image.fromarray(pixel_array)

    @staticmethod
    def extract(image): # extract hidden data by reading pixel pair differences
        pixel_array = np.array(image)
        height, width = pixel_array.shape[:2]
        bytes_data = bytearray() # stores extracted bytes
        current_byte = 0 # builds up byte from extracted bits
        bit_count = 0 # tracks bits in current byte
        
        for y in range(height):
            for x in range(0, width - 1, 2): # process pixel pairs
                for c in range(3): # check each RGB channel
                    # get pixel pair and their difference
                    p1 = pixel_array[y, x, c]
                    p2 = pixel_array[y, x + 1, c]
                    diff = abs(int(p2) - int(p1))
                    
                    # determine how many bits were embedded here
                    range_idx = PVDAlgorithm._get_range_index(diff)
                    num_bits = PVDAlgorithm.BITS_PER_RANGE[range_idx]
                    lower = PVDAlgorithm.RANGE_TABLE[range_idx][0]
                    
                    # extract the embedded bits from the difference
                    embedded = diff - lower # remove range offset to get embedded value
                    
                    for _ in range(num_bits): # extract bits one at a time
                        # shift bits left and add next bit from embedded value
                        current_byte = (current_byte << 1) | ((embedded >> (num_bits - 1)) & 1)
                        embedded <<= 1
                        bit_count += 1
                        
                        if bit_count == 8: # completed a byte
                            bytes_data.append(current_byte)
                            current_byte = 0
                            bit_count = 0
                            
                            # check for end marker once we have enough data
                            if len(bytes_data) >= 8:
                                try:
                                    text = bytes_data.decode('ascii')
                                    if '###END###' in text: # found end marker
                                        return text[:text.index('###END###')]
                                except UnicodeDecodeError:
                                    continue # keep going if we hit invalid ascii
        try:
            return bytes_data.decode('ascii') # attempt final decode of any remaining data
        except UnicodeDecodeError:
            return ''