from collections import namedtuple


class SymbolTable:
    Entry = namedtuple("Entry", ["type", "kind", "index"])

    def __init__(self):
        self.class_table = {}
        self.counters = {"static": 0, "this": 0, "argument": 0, "local": 0}

    def start_subroutine(self):
        self.subroutine_table = {}
        self.counters["argument"] = 0
        self.counters["local"] = 0

    def define(self, name: str, type: str, kind: str):
        if kind == "var":
            kind = "local"
        elif kind == "field":
            kind = "this"

        if kind in ("argument", "local"):
            self.subroutine_table[name] = self.Entry(type, kind, self.counters[kind])
        elif kind in ("static", "this"):
            self.class_table[name] = self.Entry(type, kind, self.counters[kind])

        self.counters[kind] += 1

    def var_count(self, kind: str) -> int:
        if kind == "var":
            kind = "local"
        elif kind == "field":
            kind = "this"

        return self.counters[kind]

    def kind_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name].kind

        if name in self.class_table:
            return self.class_table[name].kind

    def type_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name].type

        if name in self.class_table:
            return self.class_table[name].type

    def index_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name].index

        if name in self.class_table:
            return self.class_table[name].index