import pandas as pd

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
N = 12 # try 2000
u = 1.3
d = 0.7
S0 = 100
K = 140
alpha = 50
LAMBDA_EXERCISE = "LD"
MU_EXERCISE = "MU"
NO_EXERCISE = "NO"


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
        return (
            f"Node(\n"
            f"  key = {self.key},\n"
            f"  S = {self.S},\n"
            f"  U = {self.U},\n"
            f"  V = {self.V},\n"
            f"  X = {self.X},\n"
            f"  ex = {self.ex},\n"
            f"  depth = {self.depth}\n"
            f")"
        )
        
    
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
    
    # base case
    if node.left_key is None and node.right_key is None:
        node.X = node.V # note this is equivilent to U_N = V_N terminal case
        node.ex = LAMBDA_EXERCISE
        return
    
    # recursive case
    left_node = tree.get(node.left_key, None)
    right_node = tree.get(node.right_key, None)
    E = p * right_node.X + (1 - p) * left_node.X
    Un = node.U
    Vn = node.V

    node.X = Un if Un > E else Vn if Vn < E else E
    node.ex = LAMBDA_EXERCISE if Un > E else MU_EXERCISE if Vn < E else NO_EXERCISE
    
    
def print_tree_to_terminal(tree: dict):
    """
    Prints the tree to the terminal in a readable format.
    """
    for key, node in tree.items():
        print(f"Key: {key}, S: {node.S}, U: {node.U}, V: {node.V}, X: {node.X}, ex: {node.ex.name if node.ex else None}")


def create_df(tree: dict, attr: str) -> pd.DataFrame:
    """
    create upper triangle dataframe from the tree
    of specified attribute (S, U, V, X).
    """
    data = []
    for level in range(N + 1):
        row = [getattr(tree.get((d, level - d), None), attr, None) for d in range(level, -1, -1)]
        row.extend([None] * (N - level))
        data.append(row)
    return pd.DataFrame(data).T
    

def main():
    """
    fill out all nodes in level order from leafs to root
    print data frame
    """
    tree = {}
    keys = [(d_count, level - d_count)
            for level in range(N, -1, -1)
            for d_count in range(level + 1)]
 
    for key in keys:
        fill_SUV(tree, key)
 
    for key in keys:
        fill_Xex(tree, key)
 
    # print(tree.get((0, 0), None))
    # print(create_df(tree, 'S'))
    # print(create_df(tree, 'ex'))
            

if __name__ == "__main__":
    main()
    



