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

class Memory:
    def __init__(self):
        # 64KB total memory
        self.size = 64 * 1024 
        self.data = bytearray(self.size)

    def read_word(self, address):
        # Read a 32-bit word from memory.
        self._check_alignment(address)
        # Convert the 4 bytes at the specified address into a 32-bit integer.
        return int.from_bytes(self.data[address:address+4], byteorder='big')

    def write_word(self, address, value):
        # Write a 32-bit word to memory.
        self._check_alignment(address)
        # Ensure the value is 32-bit before packing
        value_32bit = value & 0xFFFFFFFF
        self.data[address:address+4] = value_32bit.to_bytes(4, byteorder='big')

    def _check_alignment(self, address):
        # Memory accesses must be aligned to 4 bytes for word operations.
        if address % 4 != 0:
            raise ValueError(f"Unaligned memory access at address {address}")
        if address + 4 > self.size:
            raise MemoryError(f"Memory access out of bounds at address {address}")