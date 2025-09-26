from typing import List, Optional, TextIO
from lexer import Lexer
from lexer_token import LexerToken
from Symbol import Symbol
from Table import TableStr, Table
from Rule import Rule
# Синтаксический анализатор

class Analyzer:
    def __init__(self, table: Table, grammar: List[Rule]):
        self.table = table
        self.grammar = grammar
        self.tokens: List[LexerToken] = []
        self.states: List[str] = []
        self.state_stack: List[List[Symbol]] = []
        self.token_stack: List[str] = []

    def generate_tokens_from_file(self, input_file: TextIO) -> None:
        lexer = Lexer(input_file.name)
        while True:
            token = lexer.next_token()
            if token is None:
                break
            if token.type not in ['SPACE', 'LINE_COMMENT', 'BLOCK_COMMENT']:
                self.tokens.append(token)
        lexer.close()

        if not self.tokens:
            raise RuntimeError("Input file is empty")

    def read_token(self) -> Optional[LexerToken]:
        if not self.tokens:
            return None
        return self.tokens[0]

    def pop_token(self) -> None:
        if self.tokens:
            self.tokens.pop(0)

    def get_state(self) -> Optional[str]:
        if not self.states:
            return None
        return self.states[0]

    def append_state(self, state: str) -> None:
        self.states.insert(0, state)

    def pop_state(self) -> None:
        if self.states:
            self.states.pop(0)

    def get_table_str(self, state: List[Symbol]) -> Optional[TableStr]:
        for table_str in self.table.strings:
            if state == table_str.symbols:
                return table_str
        return None

    def analyze(self, input_file: TextIO) -> None:
        self.generate_tokens_from_file(input_file)
        print(self.grammar)
        for t in self.tokens:
            print(t)

        if not self.table.strings:
            raise RuntimeError("Table is empty!")

        current_str = self.table.strings[0]
        is_analyzing = True

        while is_analyzing:
            is_state = self.get_state() is not None
            if self.read_token() is None:
                break
            symbol = self.get_state() if is_state else self.read_token().type
            value = self.get_state() if is_state else self.read_token().value

            if symbol is None:
                raise RuntimeError("Unexpected end")

            print()
            print(f"Current token: {symbol}")
            print(f"Current value: {value}")
            print("State stack: ", end="")
            for state in self.state_stack:
                for s in state:
                    print(f"{s} ", end="")
                print("|| ", end="")
            print()
            print("Token stack: ", " ".join(self.token_stack))
            print("next", current_str.next_symbols)
            next_state = current_str.next_symbols.get(symbol, [])

            if len(next_state) == 1 and next_state[0].name == "OK":
                is_analyzing = False
                continue

            if len(next_state) == 1 and next_state[0].name == "R":
                row_index = next_state[0].num_of_rule
                if row_index is None:
                    raise RuntimeError("Invalid rule number")

                row = self.grammar[row_index]  # i = i - l Пример R5(8) i = i - 8
                has_end = row.right_part[-1] == "#"

                end = len(row.right_part) - 1 if has_end else len(row.right_part)
                sliced = self.token_stack[:end]
                reversed_sliced = list(reversed(sliced))
                sliced_with_end = reversed_sliced + ["#"]

                if (symbol == "#" and row.right_part == sliced_with_end) or row.right_part == reversed_sliced:
                    state_end = len(row.right_part) - 1 if has_end else len(row.right_part)
                    self.state_stack = self.state_stack[state_end:]
                    self.token_stack = self.token_stack[state_end:]

                    self.append_state(row.non_terminal)
                    if self.state_stack:
                        current_str = self.get_table_str(self.state_stack[0])
                        if current_str is None:
                            raise RuntimeError("Unknown state")
                    else:
                        current_str = self.table.strings[0]
                    continue
                else:
                    raise RuntimeError(f"Unable to collapse expression {next_state[0]}")

            self.state_stack.insert(0, next_state)
            self.token_stack.insert(0, symbol)

            if is_state:
                self.pop_state()
            else:
                self.pop_token()

            if not self.get_table_str(next_state):
                raise RuntimeError("Unknown state")

            current_str = self.get_table_str(next_state)
            if current_str is None:
                raise RuntimeError("Invalid table state")

