class HashNode: # node class for chaining
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable: # initial implementation of a hash table
    def __init__(self, size=256):
        self.size = size
        self.table = [None] * size
        self.count = 0
    
    def _hash(self, key): # custom hash function to handle strings
        if isinstance(key, str):
            hash_value = 0
            for char in key:
                hash_value = (hash_value * 31 + ord(char)) % self.size
            return hash_value
        return key % self.size
    
    def insert(self, key, value): # insert a key-value pair
        index = self._hash(key)
        if not self.table[index]:
            self.table[index] = HashNode(key, value)
            self.count += 1
            return        
        current = self.table[index] # handle collision with chaining
        while current:
            if current.key == key:
                current.value = value # update existing key
                return
            if not current.next:
                break
            current = current.next
        current.next = HashNode(key, value)
        self.count += 1
    
    def get(self, key, default=None): # get value for a key
        index = self._hash(key)
        current = self.table[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return default
    
    def remove(self, key): # remove a key-value pair
        index = self._hash(key)
        current = self.table[index]
        prev = None
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.table[index] = current.next
                self.count -= 1
                return True
            prev = current
            current = current.next
        return False
    
    def __len__(self):
        return self.count
    
    def __contains__(self, key): # check if key exists
        return self.get(key) is not None
    
    def clear(self): # wipe the hash table
        self.table = [None] * self.size
        self.count = 0