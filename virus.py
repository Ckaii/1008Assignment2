from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries, RouteSplit
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
        """
        Select the top branch. This method makes a decision based purely on a fixed strategy
        without evaluating any properties of the branches.

        Best Case Time Complexity: O(1) - The function returns a constant result without any conditional logic or iteration.
        Worst Case Time Complexity: O(1) - Similarly, the worst case does not involve additional operations; it is constant regardless of input conditions.

        :return: BranchDecision.TOP - Always returns this decision to indicate the selection of the top branch.
        :post: decision made to select the top branch
        """
        # Always select the top branch
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Select the bottom branch. This method operates with a fixed decision logic, consistently 
        selecting the bottom route regardless of any dynamic conditions or properties of the routes.

        Best Case Time Complexity: O(1) - The function executes a fixed action that does not involve any iteration or condition beyond the return statement.
        Worst Case Time Complexity: O(1) - No variation in execution path; the complexity is constant regardless of the input scenario.

        :return: BranchDecision.BOTTOM - Consistently returns this decision, which simplifies understanding and predicting the behavior of this method.
        :post: decision made to select the bottom branch
        """
        # Always select the bottom branch
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.

        Best Case Time Complexity: O(1) - Regardless of the branch conditions, the method performs a fixed number of operations involving simple type checks and direct comparisons.
        Worst Case Time Complexity: O(1) - Even in cases where comparisons between two computers' hacking difficulties are required, the operations remain constant.

        :return: BranchDecision - Returns a decision enum based on the comparison of hacking difficulty or the route type.
        :post: decision made to select the branch with the lower hacking difficulty
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
        It evaluates the risk associated with computers on different routes and decides 
        the optimal path to minimize risk exposure.

        Best Case Time Complexity: O(1) - The complexity remains constant as the method involves fixed comparisons and a few conditional checks.
        Worst Case Time Complexity: O(1) - No loop or recursive function; the complexity is constant irrespective of the input size.

        :return: BranchDecision - Returns a decision enum based on the comparison of risk factors or path types.
        :post: Alters the navigation path of the virus according to the chosen route decision. The virus moves along the chosen branch, which can be top, bottom, or may halt if the conditions dictate so.
        """
        top_comp = top_branch.store.computer if isinstance(
            top_branch.store, RouteSeries) else None
        bot_comp = bottom_branch.store.computer if isinstance(
            bottom_branch.store, RouteSeries) else None
        # If both branches are RouteSeries, continue with additional comparisons.
        if top_comp and bot_comp:
            ret = self.compare_by_risk_factor(top_comp, bot_comp)
            if ret:
                return ret
            return self.compare_by_secret_value(top_comp, bot_comp)

        # If only one has a RouteSeries and the other a RouteSplit, pick the RouteSplit.
        # should i put .store here?
        elif isinstance(top_branch.store, RouteSeries) and isinstance(bottom_branch.store, RouteSplit):
            return BranchDecision.BOTTOM
        elif isinstance(top_branch.store, RouteSplit) and isinstance(bottom_branch.store, RouteSeries):
            return BranchDecision.TOP

        # In all other cases default to the Top path.
        return BranchDecision.TOP

    def compare_by_secret_value(self, top_comp, bot_comp):
        """
        Compare the secret values of two computers and return the appropriate BranchDecision.
        The secret value is derived by considering the hacking difficulty, hacked value, and risk factor of each computer.

        Best Case Time Complexity: O(1)
        Worst Case Time Complexity: O(1)

        :param top_comp: Computer object representing the top path's computer.
        :param bot_comp: Computer object representing the bottom path's computer.
        :return: BranchDecision - Enum indicating which path to take based on a comparative evaluation of computed secret values.
        :post: Determines the optimal path based on the secret value of the computers on each route.
        """
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

    def compare_by_risk_factor(self, top_comp, bot_comp):
        """
        Compare the risk factors of two computers and return the appropriate BranchDecision.
        If both computers have a risk factor of zero, the decision is based on the hacking difficulty.

        Best Case Time Complexity: O(1) - The function executes a finite number of comparisons which are independent of the input size.
        Worst Case Time Complexity: O(1) - Even in the most complex conditional path, the operations remain constant.

        :param top_comp: Computer object representing the top path's computer.
        :param bot_comp: Computer object representing the bottom path's computer.
        :return: BranchDecision - Enum value representing the chosen path based on the lower risk factor or, in tie cases, lower hacking difficulty.
        :post: Determines the optimal path based on the risk factor of the computers on each route.
        """
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
        return None


class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def eval_postfix(self, postfix_list):
        """
        Calculate the result of a postfix expression using a stack-based evaluation method. 
        This function supports basic arithmetic operations: addition, subtraction, multiplication, and division.

        Best Case Time Complexity: O(n) - The function needs to process each token in the list once.
        Worst Case Time Complexity: O(n) - Regardless of the content of the postfix list, each token is processed individually in a single pass through the list.
        n is the number of tokens in the postfix expression.

        :param postfix_list: List of strings, where each string is either an operand (number) or operator (+, -, *, /).
        :return: float - The result of the evaluated postfix expression.
        :post: The function evaluates the postfix expression and returns the computed result.
        """
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
        This virus employs a complex approach to decision-making, leveraging the evaluation of a postfix expression 
        to determine a threshold for making decisions.

        Best Case Time Complexity: O(n * m) - Evaluating the postfix expression where n is the number of tokens and m is the length of CALC_STR.
        Worst Case Time Complexity: O(n * m) - The complexity remains the same regardless of the scenario, as the postfix evaluation is always performed.
        
        :param top_branch: First route option.
        :param bottom_branch: Second route option.
        :return: BranchDecision - Enum value representing the chosen path.
        :post: Determines the optimal path based on the calculated threshold value and the hacking difficulty of the computers on each route.
        """
        threshold = self.eval_postfix(self.CALC_STR.split())

        top_comp = top_branch.computer if isinstance(
            top_branch, RouteSeries) else None
        bot_comp = bottom_branch.computer if isinstance(
            bottom_branch, RouteSeries) else None

        top_route = isinstance(top_branch, RouteSplit)
        bot_route = isinstance(bottom_branch, RouteSplit)

        # If both branches are RouteSeries
        if top_comp and bot_comp:
            return self.select_when_both_series(top_comp, bot_comp, threshold)
        # If one branch is RouteSeries and the other is RouteSplit
        if top_route and not bot_route:
            return BranchDecision.BOTTOM
        if not top_route and bot_route:
            return BranchDecision.TOP

        # In all other cases default to the Top path
        return BranchDecision.TOP

    def select_when_both_series(self, top_comp, bot_comp, threshold):
        """
        Decide between two RouteSeries based on the hacked values compared to a threshold.

        Best Case Time Complexity: O(1) - Direct comparisons are made without any complex computations or loops.
        Worst Case Time Complexity: O(1) - The same operations apply regardless of the input values.

        :param top_comp: Computer on the top route.
        :param bot_comp: Computer on the bottom route.
        :param threshold: Numeric threshold for decision-making derived from a complex calculation.
        :return: BranchDecision - Result of the comparison.
        """
        if top_comp.hacked_value < threshold:
            return BranchDecision.TOP
        if bot_comp.hacked_value > threshold:
            return BranchDecision.BOTTOM
        return BranchDecision.STOP
