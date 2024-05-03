from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        if sizes is not None:
            self.TABLE_SIZES = sizes

        if internal_sizes is not None:
            self.internal_sizes = internal_sizes
        else:
            self.internal_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array: ArrayR[tuple[K1, V] | None] | None = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2 | None, is_insert: bool) -> tuple[int, int] | int:
        """
        Utilize linear probing to find a suitable position for a given key or key pair in the hash table.
        Depending on whether a secondary key is provided, the function adapts its probing strategy.

        Best Case Time Complexity: O(len(key)) - Immediate location of an open slot or the target key.
        Worst Case Time Complexity: O(N * len(key)) - A full scan of the table might be required due to collisions or a nearly full table.

        :param key1: The primary key component.
        :param key2: The optional secondary key component, may be None.
        :param is_insert: Boolean flag indicating whether the operation is for insertion (True) or lookup (False).
        :return: The index of the key in the hash table if found or inserting, or a tuple with the indexes if using two keys.
        :raises KeyError: Raised if the key pair is not found in the table and `is_insert` is False, indicating a lookup operation.
        :raises FullError: Raised if the hash table is full and no slot can be accommodated for an insertion.

        Implementation Details:
        - The function first computes the hash for the primary key using a predefined hash function (`hash1`).
        - Based on whether the secondary key `key2` is provided, it calls `get_position` to handle the actual probing and placement logic:
            * If `key2` is None, it treats the operation as a single-key probe.
            * If `key2` is provided, it adjusts to a dual-key probing mechanism.
        """
        position = self.hash1(key1)

        if key2 is None:
            return self.get_position(key1, key2, is_insert, position, False)
        else:
            return self.get_position(key1, key2, is_insert, position, True)
        
    def get_position(self, key1: K1, key2: K2, is_insert: bool, position, condition) -> int:
        """
        Attempt to find the correct position for a key (or key pair) in the hash table using linear probing.
        This function efficiently manages single or dual key systems, handles insertion, and finds the positions
        for existing keys.

        Best Case Time Complexity: O(len(key))
        - The best case occurs when the slot at the initially computed hash index (from `hash1`) is either empty (for insertion) 
        or directly contains the matching key (for retrieval). This results in an immediate resolution without further probing.

        Worst Case Time Complexity: O(N * len(key))
        - The worst case occurs when the key does not initially match and the table is nearly full or the key is not present.
        The method may need to probe each slot in the table once, which means iterating through the entire table (N is the table size).

        :param key1: The primary key to be inserted or searched for.
        :param key2: The secondary key used only if the condition is True.
        :param is_insert: A boolean indicating if the operation is an insertion (True) or a search (False).
        :param position: The starting index calculated using the primary hash function.
        :param condition: A boolean that when True indicates a dual-key system is being used.
        :return: Depending on the condition, returns either an int or a tuple (int, int) representing the position(s) in the hash table.
        :raises KeyError: Raised if the key cannot be found when searching or if no empty position is found during insertion.
        """
        for _ in range(self.table_size):
            if self.array[position] is None:
                if is_insert:
                    if not condition:
                        return position
                    else:
                        self.create_internal_table(key1, position)
                else:
                    raise KeyError(key1)
                if condition:
                    index2 = self.hash2(key2, self.array[position][1])
                    return position, index2
                
            elif self.array[position][0] == key1:
                if not condition:
                    return position
                else:    
                    return position, self.array[position][1]._linear_probe(key2, is_insert)
            else:
                # Taken by something else. Time to linear probe.
                position = (position + 1) % self.table_size
            
        raise KeyError(key1)
        
    def create_internal_table(self, key1: K1, pos: int) -> None:
        """
        Creates an internal hash table for the given key1 at the given position.

        :return: None
        :post: A new LinearProbeTable is initialized and set at the specified index in the array, configured with a custom hash function.
        :comp best: O(len(key)), as initializing the LinearProbeTable, setting the hash function, and placing it in the array are all constant time operations.
        :comp worst: O(len(key)), operations do not vary as they involve fixed-time setup regardless of the input size or hash table state.
        """
        internal_table = LinearProbeTable(self.internal_sizes)
        internal_table.hash = lambda k, tab=internal_table: self.hash2(k, tab)
        self.array[pos] = (key1, internal_table)

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        Returns an iterator over keys in a hash table, which can either be top-level or nested keys based on the input key.

        :return: Iterator over keys
        :comp best: O(n) when key is None, iterates over all elements but quick skip over None entries.
        :comp worst: O(n) when key is None, each element is accessed; complexity for specified key depends on the distribution and count of entries in the nested structure which could range from O(1) to O(m).
        """
        if key is None:
            for index in range(self.table_size):
                if self.array[index] is not None:
                    yield self.array[index][0]
        
        else:
            self.iter_keys_or_values(key, 0)
        

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        Returns an iterator over values in the hash table, which can be either all values in the main table or specific values in a nested hash table based on the input key.

        :return: Iterator over values
        :comp best: O(n * m) when key is None, performs nested iterations over all slots in both main and nested tables.
        :comp worst: O(n * m) when key is None, as each non-null slot in both levels of tables is accessed; complexity for specified key depends on the distribution and count of entries in the nested structure which could range from O(1) to O(m).
        note: n is the number of elements in the main table, m is the number of elements in the nested table.
        """
        if key is None:
            for index in range(self.table_size):
                if self.array[index] is not None:
                    for j in range(self.array[index][1].table_size):
                        if self.array[index][1].array[j] is not None:
                            yield self.array[index][1].array[j][1]
        
        else:
            self.iter_keys_or_values(key, 1)

    def iter_keys_or_values(self, key: K1, get_item: int):
        """
        Returns an iterator of all keys or values in the bottom-hash-table for the given key.

        :return: Iterator of keys or values based on get_item index
        :comp best: O(N * len(key)) if the position is found quickly and the nested table is minimally filled.
        :comp worst: O(N * len(key) * m), where m is the size of the nested hash table, accounting for a full search in both tables due to collisions or fullness.
        """
        position = self._linear_probe(key, None, False)
        if position is None:
            raise KeyError(key)
        for index in range(self.array[position][1].table_size):
            if self.array[position][1].array[index] is not None:
                yield self.array[position][1].array[index][get_item]


    def keys(self, key: K1 | None = None) -> list[K1 | K2]:
        """
        Returns all keys from the hash table. If a specific key is given, returns all corresponding bottom-level keys.

        :param key: Optional. If provided, returns the keys associated with the bottom-level for the given top-level key. If None, returns all top-level keys in the table.
        :return: List of keys.
        :comp best: O(n), when key is None, where n is the size of the main hash table, for retrieving all top-level keys.
        :comp worst: O(n * m), when key is at the last index of the nested hased table, where n is the size of the main hash table and m is the size of the nested hash table, for a specific key.
        """
        res = []
        if key is None:
            for index in range(self.table_size):
                if self.array[index] is not None:
                    res.append(self.array[index][0])
        else:
            res = self.get_keys_or_values(key, 0)
        return res

    def values(self, key: K1 | None = None) -> list[V]:
        """
        Returns all values from the hash table. If a specific key is given, returns all corresponding values from the nested hash table.
        
        :return: List of values
        :comp best: O(N * len(key)), where the value to find is at the first position.
        :comp worst: O(n * m), where n is the size of the main hash table and m is the average size of the nested hash tables, for retrieving all values.
        """
        res = []
        if key is None:
            for index in range(self.table_size):
                if self.array[index] is not None:
                    for j in range(self.array[index][1].table_size):
                        if self.array[index][1].array[j] is not None:
                            res.append(self.array[index][1].array[j][1])
        else:
            res = self.get_keys_or_values(key, 1)
        return res
    
    def get_keys_or_values(self, key: K1, get_item: int) -> K1 | V:
        """
        Returns all values from the hash table. If a specific key is given, returns all corresponding values from the nested hash table.
        
        :return: List of values
        :comp best: O(N * len(key))
        :comp worst: O(N * len(key) * n)
        where n is the size of the main hash table.
        """
        res = []
        position = self._linear_probe(key, None, False)
        if position is None:
            raise KeyError(key)
        for index in range(self.array[position][1].table_size):
            if self.array[position][1].array[index] is not None:
                res.append(self.array[position][1].array[index][get_item])
        return res

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Returns all keys or values from a specified top-level key's nested hash table.
        
        :return: List of keys or values
        :comp: O(N * len(key)), where n is the size of the main hash table (due to potential full table scan by _linear_probe) and m is the size of the nested hash table.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """

        position1, position2 = self._linear_probe(key[0], key[1], False)
        return self.array[position1][1].array[position2][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.

        :complexity best: O(N * len(key)), assuming a good hash function with minimal collisions for both the main table and the sub-table or the position is empty.
        :complexity worst: O((n + (N*hash(K) + N^2*comp(K)))) * N * len(key)), where n is the number of entries in the main hash table (due to linear probing) and N^2 arises from a rehash operation triggered by a high load factor.
        """

        key1, key2 = key
        position1, position2 = self._linear_probe(key1, key2, True)
        sub_table = self.array[position1][1]

        if sub_table.is_empty():
            self.count += 1

        sub_table[key2] = data

        # resize if necessary
        if len(self) > self.table_size / 2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        :complexity best: O(n * N * len(key)) where n is the number of entries in the main table, assuming no cascading rehash is required.
        :complexity worst: O((n^2) * N * len(key)) in the worst case if every deletion triggers a cascading rehash of all subsequent entries.
        """
        position1, position2 = self._linear_probe(key[0], key[1], False)
        sub_table = self.array[position1][1]
        del sub_table[key[1]]  # Deleting the item from the sub-table

        if sub_table.is_empty():
            self.array[position1] = None
            self.count -= 1
            position1 = (position1 + 1) % self.table_size
            while self.array[position1] is not None:
                key1, sub_table = self.array[position1]
                self.array[position1] = None
                newpos = self._linear_probe(key1, None, True)
                self.array[newpos] = (key1, sub_table)
                position1 = (position1 + 1) % self.table_size

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_table = self.array  # Store the old table
        self.size_index += 1
        if self.size_index >= len(self.TABLE_SIZES):
            return

        # Create a new top-level table with the new size
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0  # Reset the count of top-level entries

        # Reinsert all entries from the old table
        for entry in old_table:
            if entry is not None:
                key1, sub_table = entry
                if len(sub_table) > sub_table.table_size / 2:
                    sub_table._rehash()

                self.array[self.hash1(key1)] = (key1, sub_table)
                self.count += 1  # Increment the count for each successfully reinserted top-level entry

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        items = []
        for entry in self.array:
            if entry is not None:
                key1, sub_table = entry
                for key2, value in sub_table:
                    items.append(f"{key1}, {key2}: {value}")
        return "\n".join(items)

