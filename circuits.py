
import eq_solver.eq_solver as eq_solver
import numpy as np
import argparse

class Node:

    __voltage : float

    __empty: bool

    def __init__(self, name_in:str) -> None:
        'Constructor of the Node class'
        
        self.name: str = name_in
        self.__supernode = False
        self.__empty = True

    def set_value(self, new_value: float) -> None:
        'Changes the value of voltage with given value, changes the empty state to false'

        self.__empty = False
        self.__voltage = new_value

    def set_to_ground(self) -> None:
        'Sets the node to ground'

        self.set_value(0.0)

    def symbolic_name(self) -> str:
        'Returns the symbolic name of the node. Used for the system of linear equations'

        if self.is_empty():
            return f"V_{self.name}"
        else:
            return f"{self.__voltage}"

    def is_empty(self) -> bool:
        'Will return true if the Node doesnt have an assigned value'

        return self.__empty

    def get_supernode(self, ) -> bool:
        
        return self.__supernode

    def get_voltage(self) -> float:

        return self.__voltage


class Ground:

    def __init__(self, ground_node: Node) -> None:
        'Constructor of the class Ground.'

        self.node: Node = ground_node

    def set_ground(self) -> None:
        'Sets the attached node to ground.'

        (self.node).set_to_ground()


class Component:

    def __init__(self, T_p_in: Node, T_n_in: Node) -> None:
        'Constructor of the class Component'
    
        self.T_p: Node = T_p_in
        self.T_n: Node = T_n_in


class Resistor(Component):

    def __init__(self, T_p: Node, T_n: Node, resistance_in: float) -> None:
        'Constructor of the class Resistor'

        super().__init__(T_p, T_n)

        self.__resistance = resistance_in

    def print_expression(self, equations: dict) -> None:
        'Writes the expression of the component in the equation of each of the terminals.'
        
        if self.T_p.is_empty():

            if self.T_p not in equations:
                equations[self.T_p] = ""

            equations[self.T_p] += f"- 1/{self.__resistance} * ({self.T_p.symbolic_name()} - {self.T_n.symbolic_name()}) "
        
        if self.T_n.is_empty():
            
            if self.T_n not in equations:
                equations[self.T_n] = ""

            equations[self.T_n] += f"+ 1/{self.__resistance} * ({self.T_p.symbolic_name()} - {self.T_n.symbolic_name()}) "

    def get_resistance(self) -> float:
        'Returns the value of the resistor.'

        return self.__resistance


class Source(Component):

    __supernode: bool

    def __init__(self, T_p: Node, T_n: Node, voltage: float) -> None:
        'Constructor of the Source class'

        super().__init__(T_p, T_n)

        self.__potential = voltage
        self.__supernode = False

    def check_reference(self, supernode_eqs: list[str]):
        'Checks if the source has a reference connected to one of its terminals. If not, its a supernode.'

        if (self.T_n.is_empty()) and (self.T_p.is_empty()):

            ## Supernode
            
            self.__supernode = True

            supernode_eqs.append(f"{self.T_p.symbolic_name()} - {self.T_n.symbolic_name()} - {self.__potential} ")
            return

        if self.T_p.is_empty():
            self.T_p.set_value( self.__potential )

        else:
            self.T_n.set_value( - self.__potential)
    
    def is_supernode(self) -> bool:
        'Checks whether the source acts as a supernode or not.'

        return self.__supernode

class Current_source(Component):

    def __init__(self, T_p_in: Node, T_n_in: Node, current_in: float) -> None:
        'Constructor for the class Current_source'
        super().__init__(T_p_in, T_n_in)

        self.__current = current_in

    def get_current(self) -> float:

        return self.__current

    def print_expression(self, equations: dict):
        'Writes the expression of the component in the equation of each of the terminals.'

            
        if self.T_p.is_empty():

            if self.T_p not in equations:
                equations[self.T_p] = ""

            equations[self.T_p] += f"+ {self.__current} "
            
        if self.T_n.is_empty():
                
            if self.T_n not in equations:
                equations[self.T_n] = ""

            equations[self.T_n] += f"- {self.__current} "

def simulate() -> list[str]:
    'Simulation function'

    nodes: list[Node] = []
    components: list = []
    sources: list[Source] = []

    equations: dict[Node, str] = {}

    list_equations: list[str] = [] # Return list
    
    ################# Simulation parameters #################

    A = Node("A")
    B = Node("B")
    C = Node("C")
    
    GND = Ground(A)
    
    U_V = Source(C, B, 5.0)
    U_1 = Current_source(A, C, 0.005)
    R_1 = Resistor(C, A, 1000)
    R_2 = Resistor(C, A, 500)
    R_3 = Resistor(A, B, 250)

    components.append(U_1)
    components.append(R_1)
    components.append(R_2)
    components.append(R_3)
    sources.append(U_V)

    ##################################

    GND.set_ground() # Works

    for source in sources:
        source.check_reference(list_equations)

    for component in components:

        component.print_expression(equations)

    # check for supernodes
    
    # excluded_nodes: list[Node] = []

    for source in sources:
        if source.is_supernode():
            list_equations.append(equations[source.T_p] + equations[source.T_n])     
            equations.pop(source.T_p)
            equations.pop(source.T_n)
        else:
            continue
    
    for node in equations:
        list_equations.append(equations[node])
    
    return list_equations


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='SIMEL', 
                                     description='Simple electronical simulator by Elias')

    parser.add_argument('-t', '--terminal', action='store_true',
                        help='print output into a .txt instead of running it to the solver.')

    args = parser.parse_args()

    terminal: bool = args.terminal

    equations: list[str] = simulate()

    if terminal:
        file = open("output.txt", 'w')

        with file as f:
            for eq in equations:
                f.write(eq)
                f.write('\n')

    else: 
        
        a: np.ndarray
        b: np.ndarray

        a, b, vars = eq_solver.parse_string_to_array(equations)

        solution = np.linalg.solve(a, b)

        eq_solver.print_output(solution, vars)




    


    
