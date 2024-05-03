from __future__ import annotations
from computer import Computer


class ComputerManager:
    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    def remove_computer(self, computer: Computer) -> None:
        self.computers.remove(computer)

    def edit_computer(self, old_computer: Computer, new_computer: Computer) -> None:
        self.remove_computer(old_computer)
        self.add_computer(new_computer)

    def computers_with_difficulty(self, diff: int) -> List[Computer]:
        return [computer for computer in self.computers if computer.hacking_difficulty == diff]

    def group_by_difficulty(self) -> List[List[Computer]]:
        if not self.computers:
            return []  # Return an empty list if no computers are stored

        diff_set = set(computer.hacking_difficulty for computer in self.computers)
        grouped_computers = []
        
        for diff in sorted(diff_set):  # Sorting the difficulties to ensure ordered groups
            grouped_computers.append(self.computers_with_difficulty(diff))
        
        return grouped_computers