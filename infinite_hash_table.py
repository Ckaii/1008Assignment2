from __future__ import annotations
from typing import Generic, TypeVar
from data_structures.linked_stack import LinkedStack

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
        self.array: ArrayR[tuple[K, V] | None] = ArrayR(self.TABLE_SIZE)
        self.count = 0
        self.level = level
    
    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        pos = self.hash(key)
        item = self.array[pos]

        if isinstance(item, InfiniteHashTable):
            return item[key]
        
        elif item is not None and item[0] == key:
            return item[1]
            
        raise KeyError("Key not found")
    
    def __setitem__(self, key: K, value: V):
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
        for item in self.array:
            if isinstance(item, tuple):
                yield item
            elif isinstance(item, InfiniteHashTable):
                yield from item.items()

    def __len__(self) -> int:
        """
        Returns the number of elements in the hash table.
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        return str(self.array)



    def get_location(self, key: K) -> list[int]:
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
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        """
        all_keys = self._gather_keys()
        all_keys.sort()
        return all_keys

    def _gather_keys(self) -> list[K]:
        """ Helper method to collect all keys from the hash table and nested hash tables. """
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