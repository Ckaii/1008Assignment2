from __future__ import annotations
from typing import Generic, TypeVar
from data_structures.linked_stack import LinkedStack
from algorithms.mergesort import mergesort
from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")


class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self, level: int = 0) -> None:
        """
        Initializes the hash table with a specified level of depth for handling collisions.

        :param level: Indicates the depth of nested hash tables, with 0 being the top level.
        :complexity: Best/Worst Case O(1), constant time to initialize internal state and array.
        :post: The hash table is initialized with the specified level and an empty array.
        """
        self.array: ArrayR[tuple[K, V] | None] = ArrayR(self.TABLE_SIZE)
        self.count = 0
        self.level = level
    
    def hash(self, key: K) -> int:
        """
        Computes a hash for the given key using a character of the key determined by the current level.

        :param key: The key to hash.
        :return: An integer representing the hashed value of the key.
        :complexity: Best/Worst Case O(1), constant time operation to compute hash.
        :post: The hash value is returned.
        """
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Retrieves the value associated with the specified key, handling nested hash tables if necessary.

        :param key: The key whose value is to be retrieved.
        :return: The value associated with the key.
        :raises KeyError: If the key is not found in the hash table.
        :complexity best: O(1), direct access if no collision or if the key directly matches.
        :complexity worst: O(N), where N is the depth of the recursion due to nested hash tables.
        """
        pos = self.hash(key)
        item = self.array[pos]

        if isinstance(item, InfiniteHashTable):
            return item[key]
        
        elif item is not None and item[0] == key:
            return item[1]
            
        raise KeyError("Key not found")
    
    def __setitem__(self, key: K, value: V):
        """
        Inserts or updates a key-value pair in the hash table.

        :param key: Key of the item to insert or update.
        :param value: Value associated with the key.
        :complexity best: O(1), when no collision occurs or if handling within a nested hash table where the key already exists or the position is none.
        :complexity worst: O(1), involves creating a new nested hash table when a collision occurs with a different key at the same position.
        :post: The key-value pair is added or updated in the hash table.
        """
        pos = self.hash(key)
        item = self.array[pos]
        
        # When no item exists at the hash position, simply add the new item.
        if item is None:
            self.array[pos] = (key, value)
            self.count += 1
        # When an item exists, check if it's another hash table.
        elif isinstance(item, InfiniteHashTable):
            # Check if the item already exists in the nested table
            if key in item:
                item[key] = value  # Update existing item without incrementing count
            else:
                item[key] = value
                self.count += 1  # Increment count only if key was not present
        else:
            # When a collision happens and it's not a nested table
            existing_key, _ = item
            if existing_key == key:
                self.array[pos] = (key, value)  # Just update the value if the same key
            else:
                # Collision with a different key, create a nested hash table
                new_table = InfiniteHashTable(self.level + 1)
                new_table[existing_key] = item[1]
                new_table[key] = value
                self.array[pos] = new_table
                # Ensure count is correctly updated: increment by 1 only as it replaces the existing item with a table
                self.count += 1

    def __delitem__(self, key: K):
        """
        Removes the specified key and its associated value from the hash table.

        :param key: The key to remove.
        :raises KeyError: If the key is not found.
        :complexity best: O(1), direct access if no deep nested structures are involved.
        :complexity worst: O(N), where N is the depth of recursion due to nested hash tables.
        :post: The key and its associated value are removed from the hash table.
        """
        pos = self.hash(key)
        item = self.array[pos]
        if item is None:
            raise KeyError(f"Key {key} not found")
        if isinstance(item, InfiniteHashTable):
            original_length = len(item)
            del item[key]
            self.count -= (original_length - len(item))
            if len(item) == 0:
                self.array[pos] = None
            elif len(item) == 1:
                for remaining_key, remaining_value in item.items():
                    self.array[pos] = (remaining_key, remaining_value)
        elif item and item[0] == key:
            self.array[pos] = None
            self.count -= 1
        else:
            raise KeyError(f"Key {key} not found")

    def items(self):
        """
        Yields all key-value pairs in the hash table, including those in nested hash tables.

        :complexity: Best/Worst Case O(n), where n is the total number of items in the table and nested tables.
        """
        for item in self.array:
            if isinstance(item, tuple):
                yield item
            elif isinstance(item, InfiniteHashTable):
                yield from item.items()

    def __len__(self) -> int:
        """
        Returns the number of elements in the hash table.

        :complexity: Best/Worst Case O(1), as the count is maintained and updated with each addition or removal.
        :return: The number of elements in the hash table.
        """
        return self.count

    def __str__(self) -> str:
        """
        Provides a string representation of the hash table.

        :complexity: Best/Worst Case O(n), where n is the total number of elements in the hash table.
        :return: String representation of the hash table.
        """
        return str(self.array)
    
    def get_location(self, key: K) -> list[int]:
        """
        Finds and records the position of the specified key through potentially multiple levels of nested hash tables.

        :param key: Key to locate in the hash table.
        :return: List of positions indicating the path taken to find the key.
        :raises KeyError: If the key is not found.
        :complexity best: O(1), if the key is found at the first position without nested tables.
        :complexity worst: O(N), where N is the depth of nested tables encountered before finding the key.
        """
        positions = []
        current_table = self

        while isinstance(current_table, InfiniteHashTable):
            pos = current_table.hash(key)
            positions.append(pos)
            item = current_table.array[pos]
            if not isinstance(item, InfiniteHashTable):
                if item is None or (isinstance(item, tuple) and item[0] != key):
                    raise KeyError("Key not found")
                break
            current_table = item
        return positions

    def __contains__(self, key: K) -> bool:
        """
        Checks whether the specified key is in the hash table, accounting for nested hash tables.

        :param key: The key to check.
        :return: True if the key exists, otherwise False.
        :complexity: Best/Worst Case O(N) in worst case, where N is the depth of nested tables that might need to be traversed.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Sorts and returns all keys in the hash table and nested hash tables in lexicographical order.

        :return: Sorted list of keys.
        :complexity: Best/Worst Case O(n log n), where n is the total number of keys, including those in nested hash tables.
        """
        return mergesort(self._gather_keys())

    def _gather_keys(self) -> list[K]:
        """
        Recursively collects all keys from the hash table and nested hash tables.

        :return: List of all keys.
        :complexity: Best Case O(n), where n is the total number of keys to be collected.
        :complexity: Worst Case O(n * m), where n is the total number of keys to be collected and m is the depth of recursion.
        """
        keys = []
        for item in self.array:
            if isinstance(item, tuple):
                keys.append(item[0])
            elif isinstance(item, InfiniteHashTable):
                keys.extend(item._gather_keys())
        return keys

if __name__ == '__main__':
    print("InfiniteHashTable")
    ih = InfiniteHashTable()
    ih["lin"] = 1

    ih["leg"] = 2
    ih["low"] = 3
    print(ih["lin"])
    print(ih["leg"])
    print(ih["low"])