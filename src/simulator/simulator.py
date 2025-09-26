from .regex_to_nfa import process_regex
from .nfa_to_dfa import process_nfa
from .minimize import process_dfa
# Регулярное выражение -> Синтаксическое дерево
# Синтаксическое дерево -> НКА
# НКА -> ДКА
# ДКА -> Минимизированный ДКА
# Минимизированный ДКА + входная строка -> результат

# Конвейер преобразования (регулярное выражение -> НКА -> ДКА -> минимизация ДКА)
def convert_regex_to_dfa(regex: str):
    nfa = process_regex(regex)
    dfa = process_nfa(*nfa)
    machine = process_dfa(dfa)
    return machine


class Simulator:
    # Инициализация симулятора с регулярными выражениями
    def __init__(self, regex: str):
        self.machine = convert_regex_to_dfa(regex)

    # Подаём входную строку на автомат и возвращаем самый длинный префикс, соответствующий регулярному выражению
    def run(self, text: str) -> str:
        states, input_symbols, transitions, outputs, initial_state = self.machine

        result = ''
        current_state = initial_state
        for symbol in text:
            if symbol not in input_symbols and 'ANY' not in input_symbols:
                return result if outputs[current_state] == 'F' else ''
            transition = transitions[current_state].get(symbol, '')
            if transition == '':
                transition = transitions[current_state].get('ANY', '')
            if transition == '':
                return result if outputs[current_state] == 'F' else ''
            result += symbol
            current_state = transition
        return result if outputs[current_state] == 'F' else ''
