from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries
from branch_decision import BranchDecision


class VirusType(ABC):

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    @abstractmethod
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        raise NotImplementedError()


class TopVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the top branch
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the bottom branch
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                return BranchDecision.TOP
            elif top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP
        # If one of them has a computer, don't take it.
        # If neither do, then take the top branch.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP


class RiskAverseVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus is risk averse and likes to choose the path with the lowest risk factor.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        # If both branches are RouteSeries, it should continue with some additional comparisons.
        if top_route and bot_route:
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer
        
            # if both computers have a risk factor of 0.0, choose the one with the lowest hacking difficulty
            if top_comp.risk_factor == 0.0 and bot_comp.risk_factor == 0.0:
                if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                    return BranchDecision.TOP 
                if top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                    return BranchDecision.BOTTOM
            
            # if only one of the computers has a risk factor of 0.0, choose that one
            if top_comp.risk_factor == 0.0:
                return BranchDecision.TOP
            if bot_comp.risk_factor == 0.0:
                return BranchDecision.BOTTOM
            
            top_value = max(top_comp.hacking_difficulty, top_comp.hacked_value / 2) / top_comp.risk_factor
            bot_value = max(bot_comp.hacking_difficulty, bot_comp.hacked_value / 2) / bot_comp.risk_factor

            # Compare the two paths and take the path with the higher value.
            if top_value < bot_value:
                return BranchDecision.TOP
            elif top_value > bot_value:
                return BranchDecision.BOTTOM
            
            # If there is a tie, take the path with the lower risk factor.
            if top_comp.risk_factor < bot_comp.risk_factor:
                return BranchDecision.TOP
            elif top_comp.risk_factor > bot_comp.risk_factor:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP

        # If only one of the branches is a RouteSeries, take the path with the RouteSplit.
        if top_route and not bot_route:
            return self.select_branch(bottom_branch.store.top, bottom_branch.store.bottom)
        if not top_route and bot_route:
            return self.select_branch(top_branch.store.top, top_branch.store.bottom)
        
        # In all other cases, take the top branch.
        else:
            return BranchDecision.TOP
        

class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus has a fancy-pants and likes to overcomplicate its approach.
        """
        pass
