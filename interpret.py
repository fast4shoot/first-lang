"""Parser

Syntactic analyzator for discovering grammar

"""
__author__ = 'ales lerch'

#import uuid
import types
from parser import Parser
from lexer import Token, untoken
from ast import Function, ast_value

class ContextValue:

    __slots__ = ("cont_val_type", "cont_val_data")

    def __init__(self, type_, data):
        self.cont_val_type = type_
        if isinstance(data, list):
            self.cont_val_data = data[0]
        else:
            self.cont_val_data = data

    def eval_cvalue(self):
        return self.cont_val_data._eval()

    @classmethod
    def unzip(data):
        if isinstance(data, ContextValue):
            return data.cont_val_data
        else:
            return data

class FunctionNotFound(Exception):

    def __init__(self, message):
        super().__init__(message)

class Interpret:

    def __init__(self, inp_file, on_interpreter=False):
        self.token = Token()
        self.parser = None
        #self.context = {}
        self.init_context()
        if on_interpreter:
            self.start_interpreter()
        else:
            self.parser = Parser(self.token.lexer(input_file=inp_file))

    def start_interpreter(self):
        while True:
            try:
                text_ = input('flang> ')
            except EOFError:
                break
            if not text_:
                continue
            parser = Parser(self.token.lexer(text=text_))
            parser.program()
            self.interpret(parser.root_ast)

    def init_context(self):
        self.context = default_functions = {
            "eval": ContextValue(
                "default", Function(
                    "eval", None, lambda x: self.context[x.value.token_value].eval_cvalue()
                )
            ),
            "+": ContextValue(
                "default", Function(
                    "+", None, lambda x, y: untoken(ast_value(x)) + untoken(ast_value(y))
                )
            ),
            "-": ContextValue(
                "default", Function(
                    "-", None, lambda x, y: untoken(ast_value(x)) - untoken(ast_value(y))
                )
            ),
            "/": ContextValue(
                "default", Function(
                    "/", None, lambda x, y: untoken(ast_value(x)) / untoken(ast_value(y))
                )
            ),
            "*": ContextValue(
                "default", Function(
                    "*", None, lambda x, y: untoken(ast_value(x)) * untoken(ast_value(y))
                )
            ),
            "stack": ContextValue(
                "default", Function(
                    "stack", None, lambda _: self.print_context_data()
                )
            ),
        }

    def print_context_data(self):
        for key, val in self.context.items():
            print(f" {key}: {val.cont_val_data.value}")

    def interpret(self, data=None, ast=[]):

        def search_function(name_of_function):
            for searching_fn in list(filter(lambda x: x.cont_val_type != "CallingFunction", self.context.values())):
                if searching_fn.cont_val_data.name == "Function" and\
                   untoken(searching_fn.cont_val_data.keyword) == name_of_function.token_value:
                    return searching_fn

            raise FunctionNotFound(f"Function {untoken(name_of_function)} not found")

        def check_context(local_cont, glob_cont, ch_val):
            try:
                return local_cont[ch_val]
            except KeyError:
                if ch_val in glob_cont:
                    return glob_cont[ch_val].cont_val_data.value
                else:
                    print(f"{ch_val} not found")

        def control_eval(fnd_func, context, set_args={}):
            for arg_number in range(len(fnd_func.cont_val_data.args)):
                set_args[untoken(fnd_func.cont_val_data.args[arg_number])] =\
                    untoken(operation.value[arg_number].value)

            func_ = check_context(
                set_args, context, untoken(fnd_func.cont_val_data.value[0].value))
            args_ = list(map(lambda f: set_args[untoken(f.value)] if untoken(f.value) in\
                set_args else untoken(f.value), fnd_func.cont_val_data.value[1:]))
            if isinstance(func_, types.LambdaType):
                print(func_(*args_))
            else:
                print(func_)

        if not data and self.parser:
            print(self.parser.program())
            ast = self.parser.root_ast
        else:
            ast = data if data else []

        for operation in ast:
            #f"{operation.keyword.value}_{str(uuid.uuid4())[:8]}"
            key = untoken(operation.keyword)
            if key in self.context and operation.name != "CallingFunction":
                print(f"Variable {key} already exits")
            elif operation.name == "CallingFunction":
                try:
                    found_fn = search_function(operation.keyword)
                except FunctionNotFound as fnf:
                    print(fnf)
                    return 1
                if found_fn.cont_val_type != "default":
                    """ if found function is defautl"""
                    control_eval(found_fn, self.context)
                else:
                    """ if found function is not defautl e.g. user made it"""
                    #print(operation, *operation.value)
                    print(found_fn.cont_val_data.value(*operation.value))
            else:
                self.context[key] = ContextValue(operation.name, operation.value)
                print(f"{operation.keyword.token_value} = {operation.value[0].name}")
        #self.print_context_data()

if __name__ == '__main__':
    Interpret(None, True).interpret()
