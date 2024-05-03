from __future__ import annotations
from algorithms.mergesort import mergesort
from algorithms.binary_search import binary_search
from computer import Computer


class ComputerOrganiser:

    def __init__(self) -> None:
        self.computers = []
        self.computers_rank_list = []

    def cur_position(self, computer: Computer) -> int:
        if computer not in self.computers:
            raise KeyError
        res = binary_search(self.computers_rank_list, computer.rank)
        return res
    
    def add_computers(self, computers: list[Computer]) -> None:
        self.computers.extend(computers)
        self.computers = mergesort(self.computers, key=lambda x: (x.hacking_difficulty, x.risk_factor, x.name))

        for i, c in enumerate(self.computers):
            c.rank = i
        
        self.computers_rank_list = [c.rank for c in self.computers]

