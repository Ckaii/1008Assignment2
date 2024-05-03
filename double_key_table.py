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
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        position = self.hash1(key1)

        if key2 is None:
            return self.get_position(key1, key2, is_insert, position, False)
            
        else:
            return self.get_position(key1, key2, is_insert, position, True)
        
    def get_position(self, key1: K1, key2: K2, is_insert: bool, position, condition) -> int:
        
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
        creates an internal hash table for the given key1 at the given position.
        """
        internal_table = LinearProbeTable(self.internal_sizes)
        internal_table.hash = lambda k, tab=internal_table: self.hash2(k, tab)
        self.array[pos] = (key1, internal_table)

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for index in range(self.table_size):
                if self.array[index] is not None:
                    yield self.array[index][0]
        
        else:
            self.iter_keys_or_values(key, 0)
        

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
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
        returns an iterator of all keys or values in the bottom-hash-table for k.
        """
        position = self._linear_probe(key, None, False)
        if position is None:
            raise KeyError(key)
        for index in range(self.array[position][1].table_size):
            if self.array[position][1].array[index] is not None:
                yield self.array[position][1].array[index][get_item]


    def keys(self, key: K1 | None = None) -> list[K1 | K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
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
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
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
        returns all top-level keys or values in the table.
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
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
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
