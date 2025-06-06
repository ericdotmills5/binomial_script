from enum import Enum

"""
Parameters:
    p: float, probability of up move
    N: int, number of periods
    u: float, up factor
    d: float, down factor
    S0: float, initial stock price
    K: float, strike price
    alpha: float, issuer cancelation fee
Returns:
    X: binary tree of game put valuation process
    lambda: binary tree of issuer's optimal stopping time
    mu: binary tree of holder's optimal stopping time
"""
global p, N, u, d, S0, K, alpha, sheet, sheet_name
p = 1/2
N = 10 # try 2000
u = 1.3
d = 0.7
S0 = 100
K = 140
alpha = 50


class Exercise(Enum):
    """
    Enum for exercise type.
    """
    
    LAMBDA_EXERCISE = 1
    MU_EXERCISE = 2
    NO_EXERCISE = 3


# class Node:
#     """
#     Complete binary tree with defined height with print to spreadsheet functionality.
#     """

#     def __init__(self, height=0, value=None, left=None, right=None, ):
#         self.value = value
#         self.ex = None
#         self.left = left
#         self.right = right
#         self.height = height

#         # initialise all nodes
#         if height > 0:
#             self.left = Node(height - 1)
#             self.right = Node(height - 1)
    
#     def __repr__(self):
#         return f"Node(value={self.value})"
    
#     # def print_to_terminal(self, indent=0):
#     #     """
#     #     Prints the tree to the terminal in a readable format.
#     #     """
#     #     print(" " * indent + str(self.ex))
#     #     if self.right:
#     #         self.right.print_to_terminal(indent + 2)
#     #     if self.left:
#     #         self.left.print_to_terminal(indent + 2)

#     def print_to_excel(self, sheet, row=0, col=0):
#         """
#         Prints the tree to the spreadsheet in a readable format.
#         """
#         sheet.cell(row=row, column=col, value=self.value)
#         sheet.cell(row=row, column=col + 1, value=self.ex.name if self.ex else None)
        
#         if self.left:
#             self.left.print_to_excel(sheet, row + 1, col)
#         if self.right:
#             self.right.print_to_excel(sheet, row + 1, col + 2)

class Node:
    """
    Symmetric binary tree hash map represntation
    """

    def __init__(self, key=None, U=None, V=None, S=None, X=None, ex=None):
        self.key = key # of the form (d_count, u_count)
        self.U = U
        self.V = V 
        self.S = S
        self.X = X
        self.ex = ex

        self.depth = sum(key)  # sum of d_count and u_count
        self.lefts = key[0]
        self.rights = key[1]
        self.left_key = (self.lefts + 1, self.rights) if self.depth < N else None
        self.right_key = (self.lefts, self.rights + 1) if self.depth < N else None

    def __repr__(self):
        return f"Node(key={self.key}, S={self.S}, U={self.U}, V={self.V}, X={self.X}, ex={self.ex.name if self.ex else None}, depth={self.depth})"

def U(S):
    """
    Value paid if issuer excersises (notice cancelation fee).
    U = (K - S)^+ + alpha
    """
    return max(K - S, 0)

def V(S):
    """
    Value paid if holder excersises.
    V = (K - S)^+
    """
    return max(K - S, 0) + alpha
    

# def fill_S(S: Node, u_count, d_count):
#     """
#     Fills S pre order with values of S0 * u^i * d^(N-i) for each node.
#     """
#     S.value = S0 * (u ** u_count) * (d ** d_count)
#     if S.left and S.right:
#         fill_S(S.left, u_count, d_count + 1)
#         fill_S(S.right, u_count + 1, d_count)


# def compute_X(X: Node, S: Node):
#     """
#     Computes value of Xn with Xn+1. 
#     Base:
#         XN = UN
#     Recursive:

#     """
#     if X.left is None and X.right is None:
#         X.value = V(S.value)
#         X.ex = Exercise.LAMBDA_EXERCISE

#     elif X.left and X.right:
#         E = p * compute_X(X.right, S.right) + (1 - p) * compute_X(X.left, S.left)
#         Un = U(S.value)
#         Vn = V(S.value)
#         if Un <= E and Vn >= E:
#             X.value = E
#             X.ex = Exercise.NO_EXERCISE
#         elif Un > E: # notice issuer takes excerise priority
#             X.value = Un
#             X.ex = Exercise.LAMBDA_EXERCISE
#         elif Vn < E:
#             X.value = Vn
#             X.ex = Exercise.MU_EXERCISE
#         # X.value = (Un if Un > E else 0) + (Vn if Vn < E else 0) + (E if Un <= E and Vn >= E else 0)

#     else:
#         assert False, "Node must have either 0 or 2 children"
    
#     return X.value

# def fill_excersise(X: Node, S: Node, excersised: Exercise = Exercise.NO_EXERCISE):
#     """
#     Fills excersise pre order with values of exercise type for each node.
#     """
#     if X.ex is None:
#         assert X.ex is not None, "Node must have exercise type"
#     elif excersised != Exercise.NO_EXERCISE:
#         X.ex = excersised
#     elif excersised == Exercise.NO_EXERCISE:
#         # X.ex = X.ex
#         pass

#     fill_excersise(X.left, S.left, X.ex) if X.left else None
#     fill_excersise(X.right, S.right, X.ex) if X.right else None

def fill_SUV(tree: dict, key: tuple):
    """
    Creates node (assumiing it does not exist) 
    Non-recurisvly fills in S, U, V values for just this node
    """
    if tree.get(key) is not None:
        assert False, "Node already exists"
    
    S = S0 * (u ** key[0]) * (d ** key[1])
    U_value = U(S)
    V_value = V(S)
    tree[key] = Node(key=key, U=U_value, V=V_value, S=S)


def fill_Xex(tree: dict, key: tuple):
    """
    Assumes that S, U, V values are already filled in for this node.
    Fills in X and ex values for just this node.
    """
    node = tree.get(key, None)
    if node is None:
        assert False, "Node does not exist"
    
    if node.X is not None:
        assert False, "Node already has X value"
    
    # base case
    if node.left_key is None and node.right_key is None:
        node.X = node.V # note this is equivilent to U_N = V_N terminal case
        node.ex = Exercise.LAMBDA_EXERCISE
        return
    
    # recursive case
    left_node = tree.get(node.left_key, None)
    right_node = tree.get(node.right_key, None)

    if left_node is None or right_node is None:
        assert False, "Left or right node does not exist"

    E = p * right_node.X + (1 - p) * left_node.X
    Un = node.U
    Vn = node.V
    
    if Un <= E and Vn >= E:
        node.X = E
        node.ex = Exercise.NO_EXERCISE
    elif Un > E:  # notice issuer takes excerise priority
        node.X = Un
        node.ex = Exercise.LAMBDA_EXERCISE
    elif Vn < E:
        node.X = Vn
        node.ex = Exercise.MU_EXERCISE
    
    
def print_tree_to_terminal(tree: dict):
    """
    Prints the tree to the terminal in a readable format.
    """
    for key, node in tree.items():
        print(f"Key: {key}, S: {node.S}, U: {node.U}, V: {node.V}, X: {node.X}, ex: {node.ex.name if node.ex else None}")
    
def main():
    """
        
    """
    # S = Node(height=N)
    # fill_S(S, 0, 0)
    # X = Node(height=N)
    # compute_X(X, S)
    # fill_excersise(X, S)

    tree = {}

    # fill in all S, U, V values in level order from bottom up
    for level in range(N, -1, -1):
        for d_count in range(level + 1):
            u_count = level - d_count
            key = (d_count, u_count)
            fill_SUV(tree, key)
    
    # print_tree_to_terminal(tree)
    
    # fill in all X, ex values in level order from bottom up
    for level in range(N, -1, -1):
        for d_count in range(level + 1):
            u_count = level - d_count
            key = (d_count, u_count)
            fill_Xex(tree, key)
    
    print(tree.get((0, 0), None))  # print root node

if __name__ == "__main__":
    main()
    



