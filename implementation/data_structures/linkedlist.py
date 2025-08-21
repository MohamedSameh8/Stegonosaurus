class ListNode:
    def __init__(self, data=None):
        self._data = data
        self._next = None

    @property
    def data(self):
        return self._data
    
    @property
    def next(self):
        return self._next
    
    @next.setter
    def next(self, value):
        self._next = value # set next node

class LinkedList:
    def __init__(self):
        self._head = None  # private head of linked list

    def append(self, data):
        new_node = ListNode(data)
        if not self._head: # if linked list is empty
            self._head = new_node # set new node as head
            return
        last = self._head # traverse to the last node
        while last.next:
            last = last.next
        last.next = new_node

    def pop(self):
        if not self._head: # if linked list is empty
            return None
        if not self._head.next: # if linked list has only one node
            data = self._head.data
            self._head = None 
            return data
        prev = None
        last = self._head # traverse to the last node
        while last.next: # find the second last node
            prev = last
            last = last.next
        prev.next = None
        return last.data # return the data of the last node

    def is_empty(self):
        return self._head is None

    def length(self):
        length = 0
        current = self._head # traverse to the last node
        while current:
            length += 1
            current = current.next # move to the next node
        return length