import os
import re
from itertools import chain
from typing import Iterator

import joblib


class Tokenizer:
    def __init__(self) -> None:
        sentenizer_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "files",
            "sent_tokenizer.joblib",
        ))
        self.nltk_sentenizer = joblib.load(sentenizer_path)

    def split_dot(self, text: str) -> str:
        # TODO: Здесь нужно написать паттерн разделения точки от заглавных букв
        _text = re.sub(r'\.([A-ZА-Я])', r'. \1', text)
        return _text

    def split_with_tokenizer(self, text):
        tokens = self.nltk_sentenizer.tokenize(text)
        return tokens

    def get_concat_rules(self):
        prev_word_patterns = '|'.join(('з\.', 'двухф\.', 'отриц\.'))
        # TODO: здесь надо написать паттерны для предыдущего предложения
        concat_rules_prev = (
            [r'\W+з\.$|двухф\.$|двухфаз.$|отриц\.$|отр\.$|вир\.$|п\.к\.$|мг.$']
        )

        begin_exceptions = '|'.join(('Tbc', 'Твс', '[\-–]'))
        # TODO: здесь надо написать паттерны соединения последющего предложения
        concat_rules_post = (
            [r'^Tbc|^Твс|^\--']
        )
        return concat_rules_prev, concat_rules_post

    def concat(self, tokens):
        _tokens = []

        concat_rules_prev, concat_rules_post = self.get_concat_rules()

        for token in tokens:
            token = [token.strip()]
            if _tokens:
                is_concated = False

                for concat_rule in concat_rules_prev:
                    if re.search(concat_rule, _tokens[-1]):
                        _tokens[-1] += f" {token.pop(0)}"
                        is_concated = True
                        break

                if not is_concated:
                    for concat_rule in concat_rules_post:
                        if re.search(concat_rule, token[0]):
                            _tokens[-1] += f" {token.pop(0)}"
                            break
            _tokens.extend(token)

        return _tokens

    def get_split_rules(self):
        # TODO: здесь нужно написать паттерны разделения предложений
        split_rules = (
            [r'\b\s*\n']
        )
        split_rules = '|'.join(split_rules)
        return split_rules

    def split_after_concatization(self, tokens):
        split_rules = self.get_split_rules()
        _tokens = chain.from_iterable([re.split(fr"{split_rules}", token)
                                       for token in tokens])
        _tokens = list(filter(None, _tokens))
        return _tokens

    def tokenize(self, text: str) -> Iterator[str]:
        _text = self.split_dot(text)
        tokens = self.split_with_tokenizer(_text)
        tokens = self.concat(tokens)
        tokens = self.split_after_concatization(tokens)
        return tokens


if __name__ == "__main__":
    text = """Пациент поступил перед МСЭК с жалобами на:
- одышку инспираторного характера при ходьбе до 150-200 метров в умеренном темпе движений по ровной местности, усиливающееся через 10-15 шагов после ускорения шага, при подъеме на 2 этаж,  купирующееся в покое
- боли в прекардиальной области, давяще-колющего характера, возникающие при работе по дому, купирующиеся в покое или изокетом
- нарастание толерантности к физической нагрузке
Ухудшение самочувствия отмечает с весны 2014 года.

АНАМНЕЗ:
 Перенесенные заболевания:
ИБС с 2008 года, Стентирование  ПМЖА в мае 2013г
ГБ, максимальный подъем до 170/90 мм рт ст, адаптированное АД 130-140/80 мм рт ст
Tbc: нет 
вир. гепатиты: нет 
ЗППП: нет 
ЯБЖ, ЯБ 12п.к. в анамнезе: нет 
Кровотечения: не были 
Гемотрансфузии: не проводились 
Аллергологический анамнез: не помнит название инъекции ( во время ожога левой кисти ) в виде крапивницы
Наследственность: отягощена по ИБС со стороны отца 
Вредные привычки: не курит"""
    tokenizer = Tokenizer()
    result = tokenizer.tokenize(text)
    print(result)
