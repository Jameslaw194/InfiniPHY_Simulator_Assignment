class CPU:
    def __init__(self, registers, memory):
        self.registers = registers
        self.memory = memory

    def _sign_extend_16(self, value):
        # Sign-extend a 16-bit immediate value to 32 bits.
        # If the 16th bit (sign bit) is 1, the number is negative.
        if value < 0:
            return value
            
        if value & 0x8000:
            return value - 0x10000
        return value

    def _update_zero_flag(self, register_index):
        # Helper method to update the condition register 'z' flag based on the value of a register.
        val = self.registers.get(register_index)
        self.registers.cr_z = (val == 0)

# --- ARITHMETIC INSTRUCTIONS ---
    
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
    
    def exec_sub(self, rd, rs, imm16=0):
        # Execute the 'sub' instruction, which subtracts the value of register rs and an optional immediate value imm16 from register rd.
        val_rd = self.registers.get(rd)
        val_rs = self.registers.get(rs)
        extended_imm = self._sign_extend_16(imm16)
        
        # Calculate result 
        result = val_rd - val_rs - extended_imm
        self.registers.set(rd, result)
        self._update_zero_flag(rd)
        
# --- MEMORY INSTRUCTIONS ---
    
    def exec_ld(self, rd, rs, off16=0):
        # Execute the 'ld' instruction, loads a word from memory into register rd. memory address is calculated as the value in register rs plus an optional offset off16.
        base_addr = self.registers.get(rs)
        offset = self._sign_extend_16(off16)
        target_addr = base_addr + offset
        
        # Read from memory and store in rd
        value = self.memory.read_word(target_addr)
        self.registers.set(rd, value)
        self._update_zero_flag(rd) # Sets cr.z if rd becomes 0, otherwise clears it

    def exec_st(self, rd, rs, off16=0):
        # Execute the 'st' instruction, stores a word from register rs into memory. memory address is calculated as the value in register rd plus an optional offset off16.
        base_addr = self.registers.get(rd)
        offset = self._sign_extend_16(off16)
        target_addr = base_addr + offset
        
        # Get the value to store from rs
        value = self.registers.get(rs)
        self.memory.write_word(target_addr, value)

    # --- BRANCHING INSTRUCTIONS ---

    def exec_j(self, ra, imm16):
        # Execute the 'j' instruction, performs an unconditional jump to the address calculated as the value in register ra plus an immediate offset imm16.
        base = self.registers.get(ra)
        offset = self._sign_extend_16(imm16)
        self.registers.pc = base + offset

    def exec_jz(self, ra, imm16):
        # Execute the 'jz' instruction, performs a conditional jump to the address calculated as the value in register ra plus an immediate offset imm16 if the zero flag (cr.z) is set.
        if self.registers.cr_z:
            base = self.registers.get(ra)
            offset = self._sign_extend_16(imm16)
            self.registers.pc = base + offset

    def exec_jnz(self, ra, imm16):
        # Execute the 'jnz' instruction, performs a conditional jump to the address calculated as the value in register ra plus an immediate offset imm16 if the zero flag (cr.z) is not set.
        if not self.registers.cr_z:
            base = self.registers.get(ra)
            offset = self._sign_extend_16(imm16)
            self.registers.pc = base + offset

    # --- BITWISE & LOGICAL INSTRUCTIONS ---

    def exec_sll(self, rd, rs, sz5, msk4=0):
        # Logical shift left with byte mask.
        val_rs = self.registers.get(rs)
        tmp = (val_rs << sz5) & 0xFFFFFFFF
        self._apply_msk4(rd, tmp, msk4)

    def exec_slr(self, rd, rs, sz5, msk4=0):
        # Logical shift right with byte mask.
        val_rs = self.registers.get(rs)
        # For logical shift right, we need to ensure that we are treating the value as unsigned.
        tmp = val_rs >> sz5 
        self._apply_msk4(rd, tmp, msk4)

    def exec_neg(self, rd, rs, msk4=0):
        # Negate with byte mask.
        val_rs = self.registers.get(rs)
        tmp = (~val_rs) & 0xFFFFFFFF
        self._apply_msk4(rd, tmp, msk4)

    def exec_and(self, rd, rs, msk16=0):
        # Logical AND.
        val_rd = self.registers.get(rd)
        val_rs = self.registers.get(rs)
        
        if msk16 == 0:
            result = val_rd & val_rs
        else:
            # msk16 is 1-extended to 32 bits
            extended_mask = msk16 | 0xFFFF0000
            result = val_rd & val_rs & extended_mask
            
        self.registers.set(rd, result)
        self._update_zero_flag(rd)

    def exec_or(self, rd, rs, msk16=0):
        # Logical OR.
        val_rd = self.registers.get(rd)
        val_rs = self.registers.get(rs)
        
        if msk16 == 0:
            result = val_rd | val_rs
        else:
            # msk16 is 0-extended to 32 bits
            result = val_rd | val_rs | msk16
            
        self.registers.set(rd, result)
        self._update_zero_flag(rd)
        
    def exec_adh(self, rd, rs):
        #Add half words, rd = rd + rs[31:16] + rs[15:0]
        val_rd = self.registers.get(rd)
        val_rs = self.registers.get(rs)
        
        # Isolate the upper and lower 16-bit half-words
        upper_half = (val_rs >> 16) & 0xFFFF
        lower_half = val_rs & 0xFFFF
        
        # Sum them into the destination register
        result = val_rd + upper_half + lower_half
        self.registers.set(rd, result)
        self._update_zero_flag(rd)

    # --- BITWISE HELPER ---

    def _apply_msk4(self, rd, tmp, msk4):
        # Helper method to apply the 4-bit mask for sll, slr, and neg instructions.
        current_rd = self.registers.get(rd)
        new_rd = current_rd
        bytes_stored = 0
        
        # Byte 0 (Bits 7:0)
        if (msk4 & 0b0001) == 0:
            new_rd = (new_rd & 0xFFFFFF00) | (tmp & 0x000000FF)
            bytes_stored |= (tmp & 0x000000FF)
            
        # Byte 1 (Bits 15:8)
        if (msk4 & 0b0010) == 0:
            new_rd = (new_rd & 0xFFFF00FF) | (tmp & 0x0000FF00)
            bytes_stored |= (tmp & 0x0000FF00)
            
        # Byte 2 (Bits 23:16)
        if (msk4 & 0b0100) == 0:
            new_rd = (new_rd & 0xFF00FFFF) | (tmp & 0x00FF0000)
            bytes_stored |= (tmp & 0x00FF0000)
            
        # Byte 3 (Bits 31:24)
        if (msk4 & 0b1000) == 0:
            new_rd = (new_rd & 0x00FFFFFF) | (tmp & 0xFF000000)
            bytes_stored |= (tmp & 0xFF000000)

        self.registers.set(rd, new_rd)
        
        # Update the zero flag based on whether any bytes were stored in rd.
        self.registers.cr_z = (bytes_stored == 0)