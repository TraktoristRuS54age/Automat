from typing import List, Optional
from dataclasses import dataclass
from Symbol import Symbol

EMPTY_SYMBOL = "e"
END_SYMBOL = "#" # маркер конца входной строки

@dataclass
class Rule: # Определяем структуру правила грамматики
    non_terminal: str # левая часть 
    right_part: List[str] # правая часть
    direction_symbols: List[Symbol] = None # список направляющих символов First/Follow

    def __post_init__(self):
        if self.direction_symbols is None:
            self.direction_symbols = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return (self.non_terminal == other.non_terminal and
                self.right_part == other.right_part and
                self.direction_symbols == other.direction_symbols)

# символ не тирминальный, если хотя бы раз встречен в левой части
def is_non_terminal(s: str, rules: List[Rule]) -> bool:
    return any(rule.non_terminal == s for rule in rules)

# получаем первое правило с этим нетерминалом слева
def get_index_of_nonterminal(rules: List[Rule], non_terminal: str) -> Optional[int]:
    for i, rule in enumerate(rules):
        if rule.non_terminal == non_terminal:
            return i
    return None

# возвращает правила с заданным нетерминалом в правой части
def get_rules_with_nonterminal(rules: List[Rule], non_terminal: str) -> List[Rule]:
    return [rule for rule in rules if non_terminal in rule.right_part]

# возвращает все правила с нетерминалом в левой части
def get_nonterminal_rules(rules: List[Rule], non_terminal: str) -> List[Rule]:
    return [rule for rule in rules if rule.non_terminal == non_terminal]
