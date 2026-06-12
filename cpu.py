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
        
# --- MEMORY INSTRUCTIONS ---
    
    def exec_ld(self, rd, rs, off16=0):
        # Execute the 'ld' instruction, which loads a word from memory into register rd. The memory address is calculated as the value in register rs plus an optional offset off16.
        base_addr = self.registers.get(rs)
        offset = self._sign_extend_16(off16)
        target_addr = base_addr + offset
        
        # Read from memory and store in rd
        value = self.memory.read_word(target_addr)
        self.registers.set(rd, value)
        self._update_zero_flag(rd) # Sets cr.z if rd becomes 0, otherwise clears it

    def exec_st(self, rd, rs, off16=0):
        # Execute the 'st' instruction, which stores a word from register rs into memory. The memory address is calculated as the value in register rd plus an optional offset off16.
        base_addr = self.registers.get(rd)
        offset = self._sign_extend_16(off16)
        target_addr = base_addr + offset
        
        # Get the value to store from rs
        value = self.registers.get(rs)
        self.memory.write_word(target_addr, value)


    # --- BRANCHING INSTRUCTIONS ---

    def exec_j(self, ra, imm16):
        # Execute the 'j' instruction, which performs an unconditional jump to the address calculated as the value in register ra plus an immediate offset imm16.
        base = self.registers.get(ra)
        offset = self._sign_extend_16(imm16)
        self.registers.pc = base + offset

    def exec_jz(self, ra, imm16):
        # Execute the 'jz' instruction, which performs a conditional jump to the address calculated as the value in register ra plus an immediate offset imm16 if the zero flag (cr.z) is set.
        if self.registers.cr_z:
            base = self.registers.get(ra)
            offset = self._sign_extend_16(imm16)
            self.registers.pc = base + offset

    def exec_jnz(self, ra, imm16):
        # Execute the 'jnz' instruction, which performs a conditional jump to the address calculated as the value in register ra plus an immediate offset imm16 if the zero flag (cr.z) is not set.
        if not self.registers.cr_z:
            base = self.registers.get(ra)
            offset = self._sign_extend_16(imm16)
            self.registers.pc = base + offset

    # --- BITWISE & LOGICAL INSTRUCTIONS ---
    # def exec_sll()
    # def exec_slr()
    # def exec_neg()
    # def exec_and()
    # def exec_or()