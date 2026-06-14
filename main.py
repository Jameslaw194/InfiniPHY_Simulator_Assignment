import sys
from hardware import Registers, Memory
from cpu import CPU

class Simulator:
    def __init__(self):
        self.registers = Registers()
        self.memory = Memory()
        self.cpu = CPU(self.registers, self.memory)
        self.instructions = []

    def load_program(self, filepath):
        # Load assembly instructions from a file into the simulator's instruction list
        with open(filepath, 'r') as f:
            # Strip comments and empty lines, and store the instructions
            self.instructions = [line.strip() for line in f if line.strip()]

    def dump_state(self):
        # Print the current state of the registers and condition flags for debugging
        print("\n--- System State ---")
        for i in range(16):
            val = self.registers.get(i)
            # output both decimal and hex for debugging
            print(f"r{i}: {val} (0x{val:08X})", end="\t" if i % 4 != 3 else "\n")
        print(f"cr.z: {self.registers.cr_z}")
        print("--------------------\n")

    def run(self):
        # Main execution loop
        # Initialize Program Counter to 0
        self.registers.pc = 0
        
        while True:
            pc = self.registers.pc
            # Calculate the instruction index based on the current PC
            idx = pc // 4 
            
            if idx < 0 or idx >= len(self.instructions):
                print(f"Halt: PC ({pc}) out of bounds or program finished.")
                break
                
            line = self.instructions[idx]
            print(f"Executing [PC: {pc}]: {line}")
            
            # Increment the program counter to point to the next instruction
            self.registers.pc += 4 
            
            self._execute_line(line)
            
            # Dump the state after executing the instruction for debugging
            self.dump_state()
            input("Press Enter to continue to next cycle...")

    def _execute_line(self, line):
        # Split the instruction line into parts, handling commas and whitespace
        parts = line.replace(',', ' ').split()
        mnemonic = parts[0]
        
        if mnemonic == 'halt':  # Special case for 'halt' instruction
            self.registers.pc = -1 
            return

        # Parse the operands and convert them to integers or register indices
        args = []
        for p in parts[1:]:
            if p.startswith('r'):
                args.append(int(p[1:]))
            elif p == 'ro':
                args.append(0)
            elif p == 'pc':
                args.append(15)
            else:
                args.append(int(p))
                
        # Execute the corresponding CPU method for the instruction
        try:
            method = getattr(self.cpu, f"exec_{mnemonic}")
            method(*args)
        except AttributeError:
            print(f"Error: Instruction '{mnemonic}' not implemented.")
            self.registers.pc = -1
        except Exception as e:
            print(f"Runtime Error on '{line}': {e}")
            self.registers.pc = -1
            
if __name__ == "__main__":
    # Initialise the simulator and load the program
    sim = Simulator()
    sim.load_program(sys.argv[1])
    sim.run()