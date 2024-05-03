from __future__ import annotations
from computer import Computer
from typing import List
from double_key_table import DoubleKeyTable
from algorithms.mergesort import mergesort
class ComputerManager:
    def __init__(self) -> None:
        self.computers = DoubleKeyTable()

    def add_computer(self, computer: Computer) -> None:
        self.computers[str(computer.hacking_difficulty), computer.name] = computer

    def remove_computer(self, computer: Computer) -> None:
        del self.computers[str(computer.hacking_difficulty), computer.name]

    def edit_computer(self, old_computer: Computer, new_computer: Computer) -> None:
        #remove the old computer and add the new computer
        del self.computers[str(old_computer.hacking_difficulty), old_computer.name]
        self.computers[str(new_computer.hacking_difficulty), new_computer.name] = new_computer

    def computers_with_difficulty(self, diff: int) -> List[Computer]:
        try:
            values = self.computers.values(str(diff))
        except KeyError:
            return []
        return values

    def group_by_difficulty(self) -> List[List[Computer]]:
        group = []
        keys = mergesort(self.computers.keys())

        for key in keys:
            group.append(self.computers.values(key))
        
        return group