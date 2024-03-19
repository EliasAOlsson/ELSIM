
import eq_solver
import argparse

class Node:

    __voltage : float

    __supernode: bool

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

    def set_to_supernode(self) -> None:
        'Converts the node in a supernode'

        self.__supernode = True

    def symbolic_name(self) -> str:
        'Returns the symbolic name of the node. Used for the system of linear equations'

        if self.is_empty():
            return f"V_{self.name}"
        else:
            return f"{self.__voltage}"

    def is_empty(self) -> bool:

        return self.__empty

    def get_supernode(self) -> bool:
        
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
        super().__init__(T_p, T_n)

        self.__resistance = resistance_in

    def print_expression(self, equations: dict) -> None:
        
        if self.T_p.is_empty():

            if self.T_p not in equations:
                equations[self.T_p] = ""

            equations[self.T_p] += f"+ 1/{self.__resistance} * ({self.T_p.symbolic_name()} - {self.T_n.symbolic_name()}) "
        
        if self.T_n.is_empty():
            
            if self.T_n not in equations:
                equations[self.T_n] = ""

            equations[self.T_n] += f"- 1/{self.__resistance} * ({self.T_p.symbolic_name()} - {self.T_n.symbolic_name()}) "

    def get_resistance(self) -> float:
        'Returns the value of the resistor.'

        return self.__resistance


class Source(Component):

    def __init__(self, T_p: Node, T_n: Node, voltage: float) -> None:
        super().__init__(T_p, T_n)

        self.__potential = voltage

    def check_reference(self, supernode_eqs: list[str]):

        if (self.T_n.is_empty()) and (self.T_p.is_empty()):

            ## Supernode
            
            self.T_n.set_to_supernode()
            self.T_p.set_to_supernode()

            supernode_eqs.append(f"{self.T_p.symbolic_name()} - {self.T_n.symbolic_name()} - {self.__potential} ")
            return

        if self.T_p.is_empty():
            self.T_p.set_value( self.__potential )

        else:
            self.T_n.set_value( - self.__potential)
   

def simulate() -> dict[Node, str]:

    nodes: list[Node] = []
    components: list = []
    sources: list[Source] = []

    equations: dict[Node, str] = {}

    supernode_equations: list[str] = []
    
    ################# Simulation parameters #################

    A = Node("A")
    B = Node("B")
    C = Node("C")
    D = Node("D")

    Gnd = Ground(D)

    U_1 = Source(A, D, 5.0)
    R1 = Resistor(B, A, 100)
    R2 = Resistor(C, B, 1000)
    R3 = Resistor(C, B, 500)
    R4 = Resistor(D, C, 1000)

    sources.append(U_1)
    components.append(R1)
    components.append(R2)
    components.append(R3)
    components.append(R4)

    ##################################
    Gnd.set_ground() # Works

    for source in sources:
        source.check_reference(supernode_equations)

    for component in components:

        component.print_expression(equations)
    
    return equations


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='SIMEL', 
                                     description='Simple electronical simulator by Elias')

    parser.add_argument('-t', '--terminal', action='store_true',
                        help='print output into a .txt instead of running it to the solver.')

    args = parser.parse_args()

    terminal: bool = args.terminal

    equations: dict[Node, str] = simulate()

    if terminal:
        file = open("output.txt", 'w')

        with file as f:
            for node in equations:
                f.write(equations[node])
                f.write('\n')

    else: 
        
        equation_list: list[str] = []

        for node in equations:
            equation_list.append(equations[node])
        
        eq_solver.solve(equation_list)





    


    
