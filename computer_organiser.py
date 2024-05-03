from __future__ import annotations
from algorithms.mergesort import mergesort
from algorithms.binary_search import binary_search
from computer import Computer


class ComputerOrganiser:

    def __init__(self) -> None:
        """
        Initializes a new instance of ComputerOrganiser.

        :complexity: Best/Worst Case O(1), constant time initialization of empty lists.
        """
        self.computers = []
        self.computers_rank_list = []

    def cur_position(self, computer: Computer) -> int:
        """
        Finds the current position of the specified computer in the sorted rank list.

        :param computer: Computer instance to find in the rank list.
        :return: The index position of the computer in the rank list.
        :raises KeyError: If the computer is not found in the computers list.

        :complexity best: O(1), where n is the middle index of the rank list.
        :complexity worst: O(log n), where n is the number of computers in the rank list using binary search.
        """
        if computer not in self.computers:
            raise KeyError
        res = binary_search(self.computers_rank_list, computer.rank)
        return res
    
    def add_computers(self, computers: list[Computer]) -> None:
        """
        Adds a list of computers to the organizer and sorts them based on defined attributes.

        :param computers: List of Computer objects to be added.

        :complexity best: O(NlogN * comp(T)), dominated by the sorting operation.
        :complexity worst: O(NlogN * comp(T)), as mergesort has a consistent complexity regardless of initial order.

        :return: None
        :post: The computers list is sorted based on hacking difficulty, risk factor, and name.
        """
        self.computers.extend(computers)
        self.computers = mergesort(self.computers, key=lambda x: (x.hacking_difficulty, x.risk_factor, x.name))

        for i, c in enumerate(self.computers):
            c.rank = i
        
        self.computers_rank_list = [c.rank for c in self.computers]

