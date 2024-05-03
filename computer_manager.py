from __future__ import annotations
from computer import Computer


class ComputerManager:
    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)
        self.computers.sort(key=lambda x: x.hacking_difficulty)

    def remove_computer(self, computer: Computer) -> None:
        self.computers.remove(computer)

    def edit_computer(self, old_computer: Computer, new_computer: Computer) -> None:
        self.remove_computer(old_computer)
        self.add_computer(new_computer)

    def computers_with_difficulty(self, diff: int) -> list[Computer]:
        return [computer for computer in self.computers if computer.hacking_difficulty == diff]

    def group_by_difficulty(self) -> list[list[Computer]]:
        res = []
        for diff in set([computer.hacking_difficulty for computer in self.computers]):
            res.append(self.computers_with_difficulty(diff))
        return res