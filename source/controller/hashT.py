from pyecore.resources import ResourceSet, URI
from pyecore.utils import dispatch

from pyecore.resources.xmi import XMIResource

from pyecore.notification import EObserver, Kind
from pyecore.ecore import EClass, EAttribute, EString, EObject, EPackage
import pyecore.ecore as ecore
from pyecore.commands import Set
import uuid # to create uuid

# based on https://www.geeksforgeeks.org/implementation-of-hash-table-in-python-using-separate-chaining/

class Node: 
	def __init__(self, key, value): 
		self.key = key 
		self.value = value 
		self.next = None


class HashTable: 
	def __init__(self, capacity): 
		self.capacity = capacity 
		self.size = 0
		self.table = [None] * capacity 

	def _hash(self, key): 
		return hash(key) % self.capacity 

	def insert(self, key, value): 
		index = self._hash(key) 

		if self.table[index] is None: 
			self.table[index] = Node(key, value) 
			self.size += 1
		else: 
			current = self.table[index] 
			while current: 
				if current.key == key: 
					current.value = value 
					return
				current = current.next
			new_node = Node(key, value) 
			new_node.next = self.table[index] 
			self.table[index] = new_node 
			self.size += 1

	def search(self, key): 
		index = self._hash(key) 

		current = self.table[index] 
		while current: 
			if current.key == key: 
				return current.value 
			current = current.next

		return False#KeyError(key)

	def remove(self, key): 
		index = self._hash(key) 

		previous = None
		current = self.table[index] 

		while current: 
			if current.key == key: 
				if previous: 
					previous.next = current.next
				else: 
					self.table[index] = current.next
				self.size -= 1
				return
			previous = current 
			current = current.next

		raise KeyError(key) 

	def __len__(self): 
		return self.size 

	def __contains__(self, key): 
		try: 
			self.search(key) 
			return True
		except KeyError: 
			return False


# Driver code 
if __name__ == '__main__': 
	
	rset = ResourceSet()
	resource = rset.get_resource(URI('simpleOO.ecore'))
	mm_root = resource.contents[0]
	rset.metamodel_registry[mm_root.nsURI] = mm_root
	resource = rset.get_resource(URI('uni.xmi'))
	Se_Mod = resource.contents[0]
	
    # Create a hash table with 
	# a capacity of 1000
	ht = HashTable(1000) 
	
	for obj in Se_Mod.eAllContents():
		print(obj._internal_id)
		ht.insert(obj._internal_id, obj) 

	
	print("1b1e1e3d507749e7ad407d8c29515145" in ht)
	xx = ht.search("880f583248bb4f32b9df040a4190b56c")
	print(xx.name)
    

	# Add some key-value pairs 
	# to the hash table 
	ht.insert("apple", 3) 
	ht.insert("banana", 2) 
	ht.insert("cherry", 5) 

	# Check if the hash table 
	# contains a key 
	print("apple" in ht) # True 
	print("durian" in ht) # False 

	# Get the value for a key 
	print(ht.search("banana")) # 2 

	# Update the value for a key 
	ht.insert("banana", 4) 
	print(ht.search("banana")) # 4 

	ht.remove("apple") 
	# Check the size of the hash table 
	print(len(ht)) # 3 
	