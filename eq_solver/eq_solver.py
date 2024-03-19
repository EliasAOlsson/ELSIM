#!/usr/bin/env python3

import numpy as np
import sympy as sp
import argparse
from sympy.parsing.sympy_parser import parse_expr


"""
Algebraic equations are sympy.core.add.Add classes

The function equations.args gives a tuple that contains the terms of the equation

If the same .args function is applied to a term, it will instead return
    a tuple with the scalar value and the variable of the term.


Analysis systems

 - Singular matrix == Sistema Compatible Indeterminado || Sistema incompatible

Workflow

 1. Create circuit

 2. Create nodes, create expressions

 3. Simplify

    3.1 The expressions might have different order of variables


 4. Create the system of linear equations (matrises)

 5. solve the system

"""

def print_ntype(thing_to_print) -> None:
    'Function for debugging purposes. It prints the value and the type of the argument.'

    print(thing_to_print)
    print("Type of the above thing{}".format(type(thing_to_print)))

def print_output(equations: list[sp.core.add.Add], solution: np.ndarray):

    for eq in equations:
        print(eq)
    
    print()

    print(solution)


def solve(lines: list[str]) -> None:
    """ 
    The main solving function. The equations are passed in string format separated by '\n' characters
    
    The solution is outputed through the terminal.

    """

    equations:list[sp.core.add.Add] = []  # List with the parsed equations

    for line in lines:
        if line == '\n':
            continue
        equations.append(parse_expr(line)) 

    eq_dict: list[dict] = []    # list that will contain the dictionaries (which contain the terms of the equations)
    variables: set[str] = set()   # The set will contain the variables of the system

    for eq in equations:
        
        dict_tmp: dict = {}

        dict_tmp['_'] = 0.0

        if isinstance(eq, sp.core.symbol.Symbol):

            dict_tmp[str(eq)] = 1.0
            eq_dict.append(dict_tmp)
            continue

        if isinstance(eq, sp.core.mul.Mul):

            dict_tmp[str(eq.args[1])] = float(eq.args[0])  # Posible optimization here
            eq_dict.append(dict_tmp)
            continue

        # Both above cases represent cases like " 3x = 0 " or " Y = 0 ". The handling of these cases 
        #   might be better handled in the circuits.py file  

        #   - study options for including these cases (Variables = 0)

        for arg in eq.args:

            if isinstance(arg, sp.core.numbers.Number):
                dict_tmp['_'] = -float(arg)
                continue

            if isinstance(arg, sp.core.symbol.Symbol):
                dict_tmp[str(arg)] = 1.0
                variables.add(str(arg))
                continue
           
            dict_tmp[str(arg.args[1])] = float(arg.args[0])
            variables.add(str(arg.args[1])) 
            
        eq_dict.append(dict_tmp) 


    b_list: list[float] = []
    a_list: list[list[float]] = []

    for eq in eq_dict:
        b_list.append(eq['_'])

    for variable in variables:

        values_current_eq: list[float] = []

        for eq in eq_dict:
            try:
               values_current_eq.append(eq[variable]) 

            except KeyError:
                values_current_eq.append(0.0)

        a_list.append(values_current_eq)

    b_np = np.array(b_list, dtype=float)

    a_np = np.array(a_list, dtype=float)

    a_np_t = np.transpose(a_np)

    print_output(equations, np.linalg.solve(a_np_t, b_np))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='Systems linear equations solver', 
                                     description='This program solves systems of linear equations in unregular format.')
    parser.add_argument('input_file')

    args = parser.parse_args()

    file: str = args.input_file

    with open(file, "r") as f:
        lines: list[str] = f.readlines()

    solve(lines)


