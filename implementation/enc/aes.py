class AESUtils:
    @staticmethod
    def _multiply_time(byte_val):
        return (((byte_val << 1) ^ 0x1B) & 0xFF) if (byte_val & 0x80) else (byte_val << 1) # returns mult of byte by 2 if less than 0x80, else returns multiplication of byte by 2 and xors result with 0x1B

    @staticmethod
    def _convert_bytes_to_matrix(data_bytes):
        return [list(data_bytes[i:i+4]) for i in range(0, len(data_bytes), 4)] # returns list of lists, 4 bytes each

    @staticmethod
    def _convert_matrix_to_bytes(matrix_data):
        return bytes(sum(matrix_data, [])) # returns bytes object of matrix data

    @staticmethod
    def _xor_two_bytes(a_bytes, b_bytes):
        return bytes(a ^ b for a, b in zip(a_bytes, b_bytes)) # returns bytes object of xor of two bytes objects

    @staticmethod
    def _apply_padding(text):
        pad_length = 16 - (len(text) % 16) # calculates padding length
        padding = bytes([pad_length] * pad_length) # creates bytes object of padding length
        return text + padding

    @staticmethod
    def _remove_padding(text):
        pad_len = text[-1] # gets last byte of text
        return text[:-pad_len] # returns text without padding

    @staticmethod
    def _divide_into_blocks(message, size=16):
        return [message[i:i+size] for i in range(0, len(message), size)] # returns list of blocks of size 16

    @staticmethod
    def _multiply_poly(a, b):
        result = 0
        while a: # while a =! 0
            if a & 1:
                result ^= b # xor result with b if a is odd
            a >>= 1 # right shift a
            b <<= 1 # left shift b
        return result

    @staticmethod
    def _modulo_polynomial(n, mod):
        while (n.bit_length()) >= (mod.bit_length()): # while n greater than or equal to mod in bit length
            shift = n.bit_length() - mod.bit_length()
            n ^= mod << shift # xor n with mod left shifted by shift
        return n

    @staticmethod
    def _galois_mult(a, b):
        product = AESUtils._multiply_poly(a, b)
        modulus = 0x11b # x^8 + x^4 + x^3 + x + 1 // 100011011
        return AESUtils._modulo_polynomial(product, modulus)

    @staticmethod
    def _galois_inverse(a): # calculates inverse of a in galois field (used for affine transformation)
        if a == 0:
            return 0
        for i in range(1, 256):
            if AESUtils._galois_mult(a, i) == 1:
                return i

    @staticmethod
    def _bitwise_dot(a, b):
        product = a & b # bitwise and of a and b
        result = 0
        while product:
            result ^= product & 1 # xor result with last bit of product
            product >>= 1 # right shift product
        return result

    @staticmethod
    def _affine_trans(matrix, vector, const):
        result = 0
        for i in range(8): 
            row = (matrix >> (8 * i)) & 0xff # get ith row of matrix
            bit = AESUtils._bitwise_dot(row, vector) # calculate dot product of ith row and vector
            result |= (bit << i) # set ith bit of result to bit
        return result ^ const # xor result with const

    @staticmethod
    def _compute_sbox(val):
        inv = AESUtils._galois_inverse(val)
        trans_matrix = int('F87C3E1F8FC7E3F1', 16) # standard rijndael affine transformation matrix, hex
        const = int('63', 16) # standard rijndael affine transformation constant, hex
        return AESUtils._affine_trans(trans_matrix, inv, const)

    @staticmethod
    def _generate_sbox(): # actual sbox generation
        sbox = [AESUtils._compute_sbox(i) for i in range(256)]
        return tuple(sbox)

    @staticmethod
    def _create_round_constants():
        constants = [0x00, 0x01] # key expansion constants
        for _ in range(2, 256):
            constants.append(AESUtils._multiply_time(constants[-1])) # appends multiplication of last element of constants with 0x02
        return tuple(constants)

    @staticmethod
    def _shift_row(matrix):
        for i in range(1, 4):
            matrix[i] = matrix[i][i:] + matrix[i][:i] # shifts ith row of matrix by i

    @staticmethod
    def _inverse_shift_row(matrix):
        for i in range(1, 4):
            matrix[i] = matrix[i][-i:] + matrix[i][:-i] # shifts ith row of matrix by -i

    @staticmethod
    def _mix_columns(state):
        for i in range(4): # for each column
            column = state[i]
            temp = column[0] ^ column[1] ^ column[2] ^ column[3] # xor of all elements of column
            original = column[0]
            column[0] ^= temp ^ AESUtils._multiply_time(column[0] ^ column[1]) # xor of temp and multiplication of first and second element of column
            column[1] ^= temp ^ AESUtils._multiply_time(column[1] ^ column[2])
            column[2] ^= temp ^ AESUtils._multiply_time(column[2] ^ column[3])
            column[3] ^= temp ^ AESUtils._multiply_time(column[3] ^ original)

    @staticmethod
    def _inverse_mix_columns(state):
        for i in range(4):
            u = AESUtils._multiply_time(AESUtils._multiply_time(state[i][0] ^ state[i][2])) # multiplication of first and third element of column
            v = AESUtils._multiply_time(AESUtils._multiply_time(state[i][1] ^ state[i][3])) 
            for j in range(4):
                state[i][j] ^= u if j % 2 == 0 else v # xor of u if j is even, else xor of v
        AESUtils._mix_columns(state)

    @staticmethod
    def _increment_bytes(a): # increments bytes by 1 - key expansion
        out = list(a) # converts a to list
        for i in reversed(range(len(out))): # for each element in out
            if out[i] != 0xFF: # if element not 0xFF (stops overflow since 0xFF + 1 = 0)
                out[i] += 1 
                break
            out[i] = 0
        return bytes(out)

    @staticmethod
    def _substitute_bytes(state, sbox):
        for i in range(4):
            state[i] = [sbox[b] for b in state[i]] # substitutes each byte in state with sbox value

    @staticmethod
    def _inverse_substitute_bytes(state, inv_sbox):
        for i in range(4):
            state[i] = [inv_sbox[b] for b in state[i]] # sub in state with inv sbox

    @staticmethod
    def _add_round_key_func(state, key):
        for i in range(4):
            state[i] = [state[i][j] ^ key[i][j] for j in range(4)] # xor of state and key

class AESAlgorithm:
    def __init__(self, key):
        self._num_rounds = 16
        self._sbox = AESUtils._generate_sbox()
        self._inv_sbox = tuple(self._sbox.index(i) for i in range(256))
        self._constants = AESUtils._create_round_constants()
        self._key_matrices = self._expand_key(key)

    def _expand_key(self, key):
        key_cols = AESUtils._convert_bytes_to_matrix(key)
        iter_size = len(key) // 4 # size of each iteration
        i = 1 # round constant index

        while len(key_cols) < (self._num_rounds + 1) * 4: # while key_cols is less than 4 * number of rounds + 1
            word = key_cols[-1][:] # last element of key_cols
            if len(key_cols) % iter_size == 0:
                word = [self._sbox[b] for b in word[1:] + word[:1]] # substitute bytes
                word[0] ^= self._constants[i]
                i += 1
            elif len(key) == 32 and len(key_cols) % iter_size == 4: # if key length is 32 and len of key_cols is multiple of 4
                word = [self._sbox[b] for b in word]
            word = AESUtils._xor_two_bytes(word, key_cols[-iter_size]) # xor of word and last element of key_cols
            key_cols.append(word)

        return [key_cols[j:j + 4] for j in range(0, len(key_cols), 4)] # returns key_cols divided into blocks of 4

    def _process_block(self, block, encrypt=True):
        state = AESUtils._convert_bytes_to_matrix(block)
        if encrypt: # if encrypting, does all steps of aes
            AESUtils._add_round_key_func(state, self._key_matrices[0])
            for rnd in range(1, self._num_rounds):
                AESUtils._substitute_bytes(state, self._sbox)
                AESUtils._shift_row(state)
                AESUtils._mix_columns(state)
                AESUtils._add_round_key_func(state, self._key_matrices[rnd])
            AESUtils._substitute_bytes(state, self._sbox)
            AESUtils._shift_row(state)
            AESUtils._add_round_key_func(state, self._key_matrices[-1])
        else: # if decrypting, does all steps of aes in reverse
            AESUtils._add_round_key_func(state, self._key_matrices[-1])
            AESUtils._inverse_shift_row(state)
            AESUtils._inverse_substitute_bytes(state, self._inv_sbox)
            for rnd in range(self._num_rounds - 1, 0, -1): # starts from last round and goes to first
                AESUtils._add_round_key_func(state, self._key_matrices[rnd])
                AESUtils._inverse_mix_columns(state)
                AESUtils._inverse_shift_row(state)
                AESUtils._inverse_substitute_bytes(state, self._inv_sbox)
            AESUtils._add_round_key_func(state, self._key_matrices[0])
        return AESUtils._convert_matrix_to_bytes(state)

    def encrypt_block(self, plaintext): # encrypts block, requires block of 16 bytes
        assert len(plaintext) == 16
        return self._process_block(plaintext, True)

    def decrypt_block(self, ciphertext): # decrypts block
        assert len(ciphertext) == 16
        return self._process_block(ciphertext, False)

    def encrypt_cbc_mode(self, plaintext, iv):
        assert len(iv) == 16
        padded = AESUtils._apply_padding(plaintext) # pads plaintext in order to make it multiple of 16
        previous = iv
        blocks = [self.encrypt_block(AESUtils._xor_two_bytes(block, previous)) for block in AESUtils._divide_into_blocks(padded)] # encrypts each block of plaintext
        encrypted_data = b''.join(blocks) # returns joined blocks
        return encrypted_data

    def decrypt_cbc_mode(self, ciphertext, iv):
        assert len(iv) == 16
        previous = iv
        blocks = [AESUtils._xor_two_bytes(previous, self.decrypt_block(block)) for block in AESUtils._divide_into_blocks(ciphertext)] # decrypts each block of ciphertext
        decrypted_data = AESUtils._remove_padding(b''.join(blocks)) # removes padding and returns joined blocks
        return decrypted_data


def aes_test():
    aes = AESAlgorithm(b"testkey123456789")
    iv = b"testiv1234567890"
    plain_text = "The quick brown fox jumps over the lazy dog!!@~$$%^&*()_+"
    cipher = aes.encrypt_cbc_mode(plain_text.encode(), iv)
    decrypted = aes.decrypt_cbc_mode(cipher, iv).decode()
    print("Encrypted:", cipher)
    print("Decrypted:", decrypted)

if __name__ == "__main__":
    aes_test()