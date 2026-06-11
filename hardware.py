class Registers:
    def __init__(self):
        # 16 general-purpose registers (r0-r15)
        self._regs = [0] * 16
        # Condition register (cr)
        self.cr_z = False  

    def get(self, index):
        # Read from a register.
        if index == 0:
            return 0  # r0 always return 0
        return self._regs[index]

    def set(self, index, value):
        # Write to a register.
        if index == 0:
            return  # Writes to r0 are ignored
        
        # Ensure the value is 32-bit before storing
        self._regs[index] = value & 0xFFFFFFFF

    # Getters and setters for the program counter (r15)
    @property
    def pc(self):
        return self.get(15)

    @pc.setter
    def pc(self, value):
        self.set(15, value)

