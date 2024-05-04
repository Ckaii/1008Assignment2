from __future__ import annotations
from computer import Computer
from typing import List
from double_key_table import DoubleKeyTable
from algorithms.mergesort import mergesort


class ComputerManager:
    def __init__(self) -> None:
        """
        Initializes a new instance of ComputerManager.
        
        :complexity: Best/Worst Case O(1), constant time initialization of the DoubleKeyTable.
        :post: The computers table is initialized as an empty DoubleKeyTable.
        """
        self.computers = DoubleKeyTable()

    def add_computer(self, computer: Computer) -> None:
        """
        Adds a new computer to the DoubleKeyTable.

        :param computer: Computer instance to be added.
        :complexity: Best/Worst Case O(1), constant time due to direct hashing and insertion.
        :post: The computer is added to the DoubleKeyTable.
        """
        self.computers[str(computer.hacking_difficulty),computer.name] = computer

    def remove_computer(self, computer: Computer) -> None:
        """
        Removes a computer from the DoubleKeyTable.

        :param computer: Computer instance to be removed.
        :complexity: Best/Worst Case O(1), constant time due to direct hashing and deletion.
        :post: The computer is removed from the DoubleKeyTable.
        """
        del self.computers[str(computer.hacking_difficulty), computer.name]

    def edit_computer(self, old_computer: Computer, new_computer: Computer) -> None:
        """
        Replaces an old computer record with a new one in the DoubleKeyTable.

        :param old_computer: The original computer to remove.
        :param new_computer: The new computer to add.
        :complexity: Best/Worst Case O(1), involves one deletion and one insertion, each at constant time.
        :post: The old computer is removed and the new computer is added to the DoubleKeyTable.
        """
        # remove the old computer and add the new computer
        del self.computers[str(
            old_computer.hacking_difficulty), old_computer.name]
        self.computers[str(new_computer.hacking_difficulty),
                       new_computer.name] = new_computer

    def computers_with_difficulty(self, diff: int) -> List[Computer]:
        """
        Retrieves a list of all computers with a specific hacking difficulty.

        :param diff: The hacking difficulty to filter by.
        :return: A list of computers, or an empty list if no match is found.
        :complexity: Best/Worst Case O(1), constant time retrieval of values.
        :post: The list of computers with the specified hacking difficulty is returned.
        """
        try:
            values = self.computers.values(str(diff))
        except KeyError:
            return []
        return values

    def group_by_difficulty(self) -> List[List[Computer]]:
        """
        Groups and returns computers by their hacking difficulty.

        :return: A list of lists of computers, grouped by hacking difficulty.
        :complexity: Best/Worst Case O(NlogN * comp(T)) for sorting the keys, followed by constant time retrieval for each group.
        """
        group = []
        keys = mergesort(self.computers.keys())

        for key in keys:
            group.append(self.computers.values(key))

        return group

