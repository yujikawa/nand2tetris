import sys
import os
from glob import glob

class Assembler:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.symbol_table = self._initialize_symbol_table()
        self.instructions = []
        self.current_address = 0

    def _initialize_symbol_table(self):
        # 初期シンボルテーブルを定義
        symbol_table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
        }
        return symbol_table

    def assemble(self):
        self._first_pass()
        self._second_pass()
        self._write_output()

    def _first_pass(self):
        # ラベルをシンボルテーブルに追加
        with open(self.input_file, 'r') as file:
            line_number = 0
            for line in file:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                if line.startswith("(") and line.endswith(")"):
                    label = line[1:-1]
                    self.symbol_table[label] = line_number
                else:
                    self.instructions.append(line)
                    line_number += 1

    def _second_pass(self):
        # 命令をバイナリコードに変換
        binary_instructions = []
        next_variable_address = 16
        for instruction in self.instructions:
            if instruction.startswith("@"):
                symbol = instruction[1:]
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if symbol not in self.symbol_table:
                        self.symbol_table[symbol] = next_variable_address
                        next_variable_address += 1
                    address = self.symbol_table[symbol]
                binary_instructions.append(f"{address:016b}")
            else:
                binary_instructions.append(self._parse_c_instruction(instruction))
        self.instructions = binary_instructions

    def _parse_c_instruction(self, instruction):
        # C命令をバイナリコードに変換
        dest, comp, jump = "null", instruction, "null"
        if "=" in instruction:
            dest, comp = instruction.split("=")
        if ";" in comp:
            comp, jump = comp.split(";")
        return "111" + self._comp(comp) + self._dest(dest) + self._jump(jump)

    def _dest(self, mnemonic):
        # destフィールドをバイナリに変換
        table = {
            "null": "000", "M": "001", "D": "010", "MD": "011",
            "A": "100", "AM": "101", "AD": "110", "AMD": "111"
        }
        return table.get(mnemonic, "000")

    def _comp(self, mnemonic):
        # compフィールドをバイナリに変換
        table = {
            "0": "0101010", "1": "0111111", "-1": "0111010",
            "D": "0001100", "A": "0110000", "!D": "0001101",
            "!A": "0110001", "-D": "0001111", "-A": "0110011",
            "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
            "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
            "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
            "M": "1110000", "!M": "1110001", "-M": "1110011",
            "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
            "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
            "D|M": "1010101"
        }
        return table.get(mnemonic, "0000000")

    def _jump(self, mnemonic):
        # jumpフィールドをバイナリに変換
        table = {
            "null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
        }
        return table.get(mnemonic, "000")

    def _write_output(self):
        # バイナリコードを出力ファイルに書き込む
        with open(self.output_file, 'w') as file:
            for instruction in self.instructions:
                file.write(instruction + '\n')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <input_dir>")
        sys.exit(1)
        
    asm_file_list = glob(os.path.join(sys.argv[1], "*.asm"))
    for asm_file in asm_file_list:
        input_file = asm_file
        output_file = os.path.splitext(asm_file)[0] + ".hack"
        assembler = Assembler(input_file, output_file)
        assembler.assemble()