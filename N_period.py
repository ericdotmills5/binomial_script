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
import random
import itertools

global p, N, u, d, S0, K, alpha, sheet, sheet_name
p = 1/2
N = 3
u = 1.1
d = 0.9
S0 = 100
K = 120
alpha = 10


class Exercise(Enum):
    """
    Enum for exercise type.
    """
    
    LAMBDA_EXERCISE = 1
    MU_EXERCISE = 2
    NO_EXERCISE = 3


class Node:
    """
    Complete binary tree with defined height with print to spreadsheet functionality.
    """

    def __init__(self, height=0, value=None, left=None, right=None, ):
        self.value = value
        self.ex = None
        self.left = left
        self.right = right
        self.height = height

        # initialise all nodes
        if height > 0:
            self.left = Node(height - 1)
            self.right = Node(height - 1)
    
    def __repr__(self):
        return f"Node(value={self.value})"
    
    def print_to_terminal(self, indent=0):
        """
        Prints the tree to the terminal in a readable format.
        """
        print(" " * indent + str(self.ex))
        if self.right:
            self.right.print_to_terminal(indent + 2)
        if self.left:
            self.left.print_to_terminal(indent + 2)


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
    

def fill_S(S: Node, u_count, d_count):
    """
    Fills S pre order with values of S0 * u^i * d^(N-i) for each node.
    """
    S.value = S0 * (u ** u_count) * (d ** d_count)
    if S.left and S.right:
        fill_S(S.left, u_count, d_count + 1)
        fill_S(S.right, u_count + 1, d_count)


def compute_X(X: Node, S: Node):
    """
    Computes value of Xn with Xn+1. 
    Base:
        XN = UN
    Recursive:

    """
    if X.left is None and X.right is None:
        X.value = V(S.value)
        X.ex = Exercise.LAMBDA_EXERCISE

    elif X.left and X.right:
        E = p * compute_X(X.right, S.right) + (1 - p) * compute_X(X.left, S.left)
        Un = U(S.value)
        Vn = V(S.value)
        if Un <= E and Vn >= E:
            X.value = E
            X.ex = Exercise.NO_EXERCISE
        elif Un > E: # notice issuer takes excerise priority
            X.value = Un
            X.ex = Exercise.LAMBDA_EXERCISE
        elif Vn < E:
            X.value = Vn
            X.ex = Exercise.MU_EXERCISE
        # X.value = (Un if Un > E else 0) + (Vn if Vn < E else 0) + (E if Un <= E and Vn >= E else 0)

    else:
        assert False, "Node must have either 0 or 2 children"
    
    return X.value


def fill_excersise(X: Node, S: Node, excersised: Exercise = Exercise.NO_EXERCISE):
    """
    Fills excersise pre order with values of exercise type for each node.
    """
    if X.ex is None:
        assert X.ex is not None, "Node must have exercise type"
    elif excersised != Exercise.NO_EXERCISE:
        X.ex = excersised
    elif excersised == Exercise.NO_EXERCISE:
        # X.ex = X.ex
        pass

    fill_excersise(X.left, S.left, X.ex) if X.left else None
    fill_excersise(X.right, S.right, X.ex) if X.right else None
    

def main():
    """
        
    """
    # try a variety of combinations of parameters
    # p_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # N_list = [4, 5, 6, 7, 8, 9, 10]
    u_list = [1.1, 1.2, 1.3, 1.4, 1.5]
    d_list = [0.9, 0.8, 0.7, 0.6, 0.5]
    K_list = [100, 120, 140, 160]
    alpha_list = [0.001, 0.01, 0.1]

    # combinations = list(itertools.product(p_list, N_list, u_list, d_list, K_list, alpha_list))
    combinations = list(itertools.product(u_list, d_list, K_list, alpha_list))
    random.shuffle(combinations)
    
    global p, N, u, d, S0, K, alpha

    i = 0
    j = 0
    # for (p_val, N_val, u_val, d_val, K_val, alpha_val) in combinations:
    for (u_val, d_val, K_val, alpha_val) in combinations:
        
        N = 20 # N_val
        u = u_val
        d = d_val
        K = K_val
        p = (1 - d_val) / (u_val - d_val) # p_val
        alpha = alpha_val # alpha_val

        S = Node(height=N)
        fill_S(S, 0, 0)
        X = Node(height=N)
        compute_X(X, S)
        fill_excersise(X, S)
        
        if X.ex == Exercise.NO_EXERCISE:
            print(f"{j}th {X.ex} for parameters (p={p}, N={N}, u={u}, d={d}, K={K}, alpha={alpha})")
            j += 1
        
        i += 1
    
    print(i, "combinations processed.")
        



    

if __name__ == "__main__":
    main()
    



