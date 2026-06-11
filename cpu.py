class CPU:
    def __init__(self, registers, memory):
        self.registers = registers
        self.memory = memory

    def _sign_extend_16(self, value):
        # Sign-extend a 16-bit immediate value to 32 bits.
        # If the 16th bit (sign bit) is 1, the number is negative.
        if value & 0x8000:
            return value - 0x10000
        return value

    def _update_zero_flag(self, register_index):
        # Helper method to update the condition register 'z' flag based on the value of a register.
        val = self.registers.get(register_index)
        self.registers.cr_z = (val == 0)

# --- INSTRUCTION EXECUTORS ---
    
    def exec_add(self, rd, rs, imm16=0):
        # Execute the 'add' instruction, which adds the value of register rs and an optional immediate value imm16 to register rd.
        val_rd = self.registers.get(rd)
        val_rs = self.registers.get(rs)
        extended_imm = self._sign_extend_16(imm16)
        
        # Perform the addition and store the result in rd
        result = val_rd + val_rs + extended_imm
        self.registers.set(rd, result)
        
        # Update the zero flag based on the result in rd
        self._update_zero_flag(rd)