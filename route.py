from __future__ import annotations
import copy
from dataclasses import dataclass

from branch_decision import BranchDecision
from computer import Computer

from typing import TYPE_CHECKING, Union
from data_structures.linked_stack import LinkedStack

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from virus import VirusType


@dataclass
class RouteSplit:
    """
    A split in the route.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Route
    bottom: Route
    following: Route

    def remove_branch(self) -> RouteStore:
        """Removes the branch, should just leave the remaining following route."""
        return self.following.store

@dataclass
class RouteSeries:
    """
    A computer, followed by the rest of the route

    --computer--following--

    """

    computer: Computer
    following: Route

    def remove_computer(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Removing the computer at the beginning of this series.
        """
        if not self.computer:
            raise ValueError("No computer to remove")
        return RouteSeries(None, self.following)

    def add_computer_before(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer in series before the current one.
        """
        return RouteSeries(computer, Route(self))

    def add_computer_after(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, Route(RouteSeries(computer, self.following)))


    def add_empty_branch_before(self) -> RouteStore:
        """Returns a route store which would be the result of:
        Adding an empty branch, where the current routestore is now the following path.
        """
        return RouteSplit(Route(None), Route(None), Route(self))

    def add_empty_branch_after(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, Route(RouteSplit(Route(None), Route(None), self.following)))


RouteStore = Union[RouteSplit, RouteSeries, None]


@dataclass
class Route:

    store: RouteStore = None

    def add_computer_before(self, computer: Computer) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding a computer before everything currently in the route.

        """
        return Route(RouteSeries(computer, self))

    def add_empty_branch_before(self) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding an empty branch before everything currently in the route.
        """
        return Route(RouteSplit(Route(None), Route(None), self))

    def follow_path(self, virus_type: VirusType) -> None:
        """
        Navigate through a network route, making decisions at branches and adding computers based on the virus_type's strategy. 
        This method uses a stack to manage branch paths for backtracking, ensuring all viable paths are explored according to decision criteria.

        Best Case Time Complexity: O(n) - Occurs when each branch decision is processed exactly once and each decision involves evaluating a postfix expression.
        Worst Case Time Complexity: O(n * (n1 * m)) - Occurs when FancyVirus was chosen.
        n is the number of computers in the route, n1 is the number of tokens and m is the length of CALC_STR.

        :return: None
        :post: All accessible computers in the route are processed according to the virus_type, and the internal state of the route (i.e., the current position within the network) is updated based on the path taken.
        """
        temp_store = self.store
        temp_stack = LinkedStack()
        while True:
            if isinstance(temp_store, RouteSplit):
                decision = virus_type.select_branch(temp_store.top, temp_store.bottom)
                temp_stack.push(temp_store.remove_branch())
                if decision == BranchDecision.TOP:
                    temp_store = temp_store.top.store
                elif decision == BranchDecision.BOTTOM:
                    temp_store= temp_store.bottom.store
                else:
                    break

            elif isinstance(temp_store, RouteSeries):
                virus_type.add_computer(temp_store.computer)
                if temp_store.following.store is not None:
                    temp_store = temp_store.following.store
                elif not temp_stack.is_empty():
                    temp_store = temp_stack.pop()
                else:
                    break
            else:
                temp_store = temp_stack.pop()
        

    def add_all_computers(self) -> list[Computer]:
        """
        Recursively collects all computers present in the route structure. This method traverses different types
        of routes and compiles a list of all computers found along the way.

        Best Case Time Complexity: O(n) - This is when the route has a straightforward, linear series of computers without any splits.
        Worst Case Time Complexity: O(n) - Even with splits, each computer in the route is processed exactly once.
        n is the total number of computers or the depth of recursion.

        :return: list[Computer] - A list containing all computers collected from the route.
        "post": The route structure remains unchanged.
        """
        if type(self.store) == RouteSplit:
            return self.store.top.add_all_computers() + self.store.bottom.add_all_computers() + self.store.following.add_all_computers()
            
        elif type(self.store) == RouteSeries:
            return [self.store.computer] + self.store.following.add_all_computers()

        else:
            return []
    
    
