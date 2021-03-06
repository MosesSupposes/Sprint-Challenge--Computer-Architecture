"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    commands = {
        "HLT": 0b00000001,
        "LDI": 0b10000010,
        "PRN": 0b01000111,
        "ADD": 0b10100000,
        "MUL": 0b10100010,
        "PUSH": 0b01000101,
        "POP": 0b01000110,
        "CALL": 0b01010000,
        "RET": 0b00010001,
        "CMP": 0b10100111,
        "JMP": 0b01010100,
        "JEQ": 0b01010101,
        "JNE": 0b01010110,
        "AND": 0b10101000,
        "OR": 0b10101010,
        "XOR": 0b10101011,
        "NOT": 0b01101001,
        "SHL": 0b10101100,
        "SHR": 0b10101101,
        "MOD": 0b10100100
    }

    commands_inverted = {
        0b00000001: "HLT",
        0b10000010: "LDI",
        0b01000111: "PRN",
        0b10100000: "ADD",
        0b10100010: "MUL",
        0b01000101: "PUSH",
        0b01000110: "POP",
        0b01010000: "CALL",
        0b00010001: "RET",
        0b10100111: "CMP",
        0b01010100: "JMP",
        0b01010101: "JEQ",
        0b01010110: "JNE",
        0b10101000: "AND",
        0b10101010: "OR",
        0b10101011: "XOR",
        0b01101001: "NOT",
        0b10101100: "SHL",
        0b10101101: "SHR",
        0b10100100: "MOD"
    }

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 
        self.reg = [0] * 8
         # Initialize the stack pointer. R7 is the dedicated stack pointer.
        self.reg[7] = 0xf4
        self.pc = 0
        self.fl = 0b00000000
        self.branch_table = {
            "HLT": self.HLT,
            "LDI": self.LDI,
            "PRN": self.PRN,
            "ADD": self.ADD,
            "MUL": self.MUL,
            "PUSH": self.PUSH,
            "POP": self.POP,
            "CALL": self.CALL,
            "RET": self.RET,
            "CMP": self.CMP,
            "JMP": self.JMP,
            "JEQ": self.JEQ,
            "JNE": self.JNE,
            "AND": self.AND,
            "OR": self.OR,
            "XOR": self.XOR,
            "NOT": self.NOT,
            "SHL": self.SHL,
            "SHR": self.SHR,
            "MOD": self.MOD
        }

    def load(self, program):
        """Load a program into memory."""
        address = 0
        try: 
            with open(program) as p:
                for instruction in p:
                    instruction = instruction.strip().split("#")[0]
                    if instruction != "":
                        self.ram_write(address, int(instruction, 2))
                        address += 1
        except Exception:
            raise ValueError("Invalid file path.")

    def ram_read(self, address): 
        try: 
            return self.ram[address]
        except IndexError:
            raise ValueError("The address of value  " + str(address) +  " isn't a valid location in memory")
    
    def ram_write(self, address, value):
        self.ram[address] = value
        return value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == "AND": 
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        
        elif op == "XOR": 
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        
        elif op == "NOT":
            self.reg[reg_a] = (lambda n, numbits=8: (1 << numbits) - 1 - n)(self.reg[reg_a])
        
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                print("Can't perfrom a MOD operation on a zero value")
                self.ram[self.pc + 3] = self.commands["HLT"]
            else:
                self.reg[reg_a] %=  self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        self.pc += 1
        sys.exit(0) 

    def LDI(self):
        self.reg[self.ram[self.pc + 1]] = self.ram[self.pc + 2]
        self.pc += 3
    
    def PRN(self):
        print(self.reg[self.ram[self.pc + 1]])
        self.pc += 2

    def ADD(self):
        self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def MUL(self):
        self.alu("MUL", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def AND(self):
        self.alu("AND", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def OR(self):
        self.alu("OR", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def XOR(self):
        self.alu("XOR", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def NOT(self):
        # Passing in the same value to both arguments is intentional. 
        # The "NOT" operator only needs one register, unlike other ALU operations.
        self.alu("NOT", self.ram[self.pc + 1], self.ram[self.pc + 1])
        self.pc += 2
    
    def SHL(self):
        self.alu("SHL", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def SHR(self):
        self.alu("SHR", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def MOD(self):
        self.alu("MOD", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def PUSH(self):
        # The seventh register is dedicated to keeping track of the stack pointer
        SP = 7
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.reg[self.ram[self.pc + 1]]

        self.pc += 2
    
    def POP(self):
        # The seventh register is dedicated to keeping track of the stack pointer
        SP = 7 
        self.reg[self.ram[self.pc + 1]] = self.ram[self.reg[SP]]
        self.reg[SP] += 1

        self.pc += 2
    
    def CALL(self):
        SP = 7
        self.reg[SP] -= 1
        # Push the return address onto the stack
        self.ram[self.reg[SP]] = self.pc + 2
        # Jump to the pc held in the given register
        self.pc = self.reg[self.ram[self.pc + 1]]
    
    def RET(self):
        SP = 7 
        address_to_jump_to = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = address_to_jump_to
    
    def CMP(self): 
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        
        # Flag placeholders: 00000LGE
        if self.reg[reg_a] < self.reg[reg_b]:
            self.fl = 0b00000100
        elif self.reg[reg_a] > self.reg[reg_b]:
            self.fl = 0b00000010
        # If the two registers are equal in value...
        else:
            self.fl = 0b00000001

        self.pc += 3
    
    def JMP(self):
        register_containing_register_to_jump_to = self.ram[self.pc + 1]
        self.pc = self.reg[register_containing_register_to_jump_to]
    
    def JEQ(self):
        register_containing_register_to_jump_to = self.ram[self.pc + 1]
        # If the equal flag is set to true...
        if self.fl == 0b00000001:
            self.pc = self.reg[register_containing_register_to_jump_to]
        else:
            self.pc += 2
    
    def JNE(self):
        register_containing_register_to_jump_to = self.ram[self.pc + 1]
        if self.fl != 0b00000001:
            self.pc = self.reg[register_containing_register_to_jump_to]
        else:
            self.pc += 2


    def run(self):
        """Run the CPU."""
        IR = None
        while IR != self.commands["HLT"]:
            IR = self.ram_read(self.pc)

            if IR in self.commands_inverted:
                self.branch_table[self.commands_inverted[IR]]()
            else:
                raise Exception(f"Invalid Command: {IR}")
        
        # Reset the program counter
        self.pc = 0
