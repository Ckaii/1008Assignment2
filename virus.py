from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries,RouteSplit
from branch_decision import BranchDecision
from data_structures.linked_stack import LinkedStack


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
        top_comp = top_branch.store.computer if isinstance(top_branch.store, RouteSeries) else None
        bot_comp = bottom_branch.store.computer if isinstance(bottom_branch.store, RouteSeries) else None
        print(top_comp)
        print(bot_comp)
        # If both branches are RouteSeries, continue with additional comparisons.
        if top_comp and bot_comp:
            # If any computer has a risk factor of 0.0, take that path.
            if top_comp.risk_factor == 0.0 and bot_comp.risk_factor != 0.0:
                return BranchDecision.TOP
            elif bot_comp.risk_factor == 0.0 and top_comp.risk_factor != 0.0:
                return BranchDecision.BOTTOM
            elif top_comp.risk_factor == 0.0 and bot_comp.risk_factor == 0.0:
                # If there are multiple computers with a risk_factor of 0.0, take the path with the lowest hacking difficulty.
                if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                    return BranchDecision.TOP
                elif bot_comp.hacking_difficulty < top_comp.hacking_difficulty:
                    return BranchDecision.BOTTOM

            # Take the highest value between the hacking_difficulty and the half of the hacked_value.
            top_value = max(top_comp.hacking_difficulty, top_comp.hacked_value / 2)
            bot_value = max(bot_comp.hacking_difficulty, bot_comp.hacked_value / 2)

            # Then, divide this by the risk factor.
            if top_comp.risk_factor != 0.0:
                top_value /= top_comp.risk_factor
            if bot_comp.risk_factor != 0.0:
                bot_value /= bot_comp.risk_factor

            # Compare the two paths and take the path with the higher value.
            if top_value > bot_value:
                return BranchDecision.TOP
            elif bot_value > top_value:
                return BranchDecision.BOTTOM
            else:
                # If there is a tie, take the path with the lower risk factor.
                if top_comp.risk_factor < bot_comp.risk_factor:
                    return BranchDecision.TOP
                elif bot_comp.risk_factor < top_comp.risk_factor:
                    return BranchDecision.BOTTOM
                else:
                    return BranchDecision.STOP

        # If only one has a RouteSeries and the other a RouteSplit, pick the RouteSplit.
        elif isinstance(top_branch.store, RouteSeries) and isinstance(bottom_branch.store, RouteSplit):#should i put .store here?
            return BranchDecision.BOTTOM
        elif isinstance(top_branch.store, RouteSplit) and isinstance(bottom_branch.store, RouteSeries):
            return BranchDecision.TOP

        # In all other cases default to the Top path.
        return BranchDecision.TOP

class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"
    
    def eval_postfix(self, postfix_list):
        # creating a new stack!
        stack = LinkedStack()

        for token in postfix_list:
            if token.isdigit():
                stack.push(float(token))
            else:
                op1 = stack.pop()
                op2 = stack.pop()

                if token == '+':
                    res = op2 + op1
                elif token == '-':
                    res = op2 - op1
                elif token == '*':
                    res = op2 * op1
                else:  # token == '/'
                    res = op2 / op1

                stack.push(res)
        return stack.pop()

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus has a fancy-pants and likes to overcomplicate its approach.
        """
        threshold = self.eval_postfix(self.CALC_STR.split())

        top_comp = top_branch.computer if isinstance(top_branch, RouteSeries) else None
        bot_comp = bottom_branch.computer if isinstance(bottom_branch, RouteSeries) else None
    
        top_route = isinstance(top_branch, RouteSplit)
        bot_route = isinstance(bottom_branch, RouteSplit)
    
        # If both branches are RouteSeries
        if top_comp and bot_comp:
            if top_comp.hacked_value < threshold:
                return BranchDecision.TOP
            if bot_comp.hacked_value > threshold:
                return BranchDecision.BOTTOM
            return BranchDecision.STOP
    
        # If one branch is RouteSeries and the other is RouteSplit
        if top_route and not bot_route:
            return BranchDecision.BOTTOM
        if not top_route and bot_route:
            return BranchDecision.TOP
    
        # In all other cases default to the Top path
        return BranchDecision.TOP
