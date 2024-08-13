import re
import sys

# Define token types
TOKEN = [
    ('STRING', r'\".*\"'),
    ('PRINT', r'print'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('EQUALS', r'='),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('INPUT', r'input'),
    ('IMPORT', r'use'),
    ('FUNCTION', r'fc'),
    ('INCREMENT', r'\+\+'),
    ('DECREMENT', r'--'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULTIPLY', r'\*'),
    ('DIVIDE', r'/'),
    ('NUMBER', r'\d+'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('EQ', r'=='),
    ('NEQ', r'!='),
    ('LT', r'<'),
    ('GT', r'>'),
    ('LTE', r'<='),
    ('GTE', r'>=')
]

debug_mode = False # Set this to True to enable debug prints

def tokenize(program):
    tokens = []
    line_number = 1
    for line in program:
        while line:
            match = None
            for token_type, pattern in TOKEN:
                regex = re.compile(pattern)
                match = regex.match(line)
                if match:
                    tokens.append((token_type, match.group(0), line_number))
                    line = line[match.end():].strip()
                    break
            if not match:
                raise SyntaxError(f'Unexpected character: {line[0]} on line {line_number}')
        line_number += 1
    if debug_mode:
        print("Tokens:", tokens) 
    return tokens
def parse(tokens):
    index = 0
    ast = []

    def parse_expression(index):
        token_type, token_value, line_number = tokens[index]
        if token_type == 'STRING':
            return token_value, index + 1
        elif token_type == 'NUMBER':
            return int(token_value), index + 1
        elif token_type == 'IDENTIFIER':
            left_expr = token_value
            index += 1
            if index < len(tokens) and tokens[index][0] in ('PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO'):
                op = tokens[index][0]
                index += 1
                right_expr, index = parse_expression(index)
                return ('BINARY_OP', left_expr, op, right_expr), index
            return left_expr, index
        raise SyntaxError(f"Invalid expression on line {line_number}")

    def parse_condition(index):
        if tokens[index][0] == 'LPAREN':
            index += 1
            left_expr, index = parse_expression(index)
            op = tokens[index][1]
            index += 1
            right_expr, index = parse_expression(index)
            if tokens[index][0] == 'RPAREN':
                return ('CONDITION', left_expr, op, right_expr), index + 1
        line_number = tokens[index][2]
        raise SyntaxError(f"Invalid condition on line {line_number}")

    def parse_statement(index):
        token_type, token_value, line_number = tokens[index]
        if debug_mode:
            print(f"Parsing statement: {token_type}, {token_value} on line {line_number}")  # Debug print
        if token_type == 'PRINT':
            index += 1
            expr, index = parse_expression(index)
            if tokens[index][0] == 'SEMICOLON':
                return ('PRINT', expr), index + 1
        elif token_type == 'IDENTIFIER':
            var_name = token_value
            index += 1
            if tokens[index][0] == 'EQUALS':
                index += 1
                expr, index = parse_expression(index)
                if tokens[index][0] == 'SEMICOLON':
                    return ('ASSIGN', var_name, expr), index + 1
            elif tokens[index][0] == 'INCREMENT':
                index += 1
                if tokens[index][0] == 'SEMICOLON':
                    return ('INCREMENT', var_name), index + 1
            elif tokens[index][0] == 'DECREMENT':
                index += 1
                if tokens[index][0] == 'SEMICOLON':
                    return ('DECREMENT', var_name), index + 1
            elif tokens[index][0] == 'LPAREN':
                index += 1
                call_args = []
                while tokens[index][0] != 'RPAREN':
                    arg, index = parse_expression(index)
                    call_args.append(arg)
                    if tokens[index][0] == 'COMMA':
                        index += 1
                index += 1
                if tokens[index][0] == 'SEMICOLON':
                    return ('CALL', var_name, call_args), index + 1
        elif token_type == 'IF':
            index += 1
            condition, index = parse_condition(index)
            if tokens[index][0] == 'LBRACE':
                index += 1
                if_body = []
                while tokens[index][0] != 'RBRACE':
                    stmt, index = parse_statement(index)
                    if_body.append(stmt)
                index += 1
                else_body = []
                if index < len(tokens) and tokens[index][0] == 'ELSE':
                    index += 1
                    if tokens[index][0] == 'LBRACE':
                        index += 1
                        while tokens[index][0] != 'RBRACE':
                            stmt, index = parse_statement(index)
                            else_body.append(stmt)
                        index += 1
                return ('IF', condition, if_body, else_body), index
        elif token_type == 'WHILE':
            index += 1
            condition, index = parse_condition(index)
            if tokens[index][0] == 'LBRACE':
                index += 1
                body = []
                while tokens[index][0] != 'RBRACE':
                    stmt, index = parse_statement(index)
                    body.append(stmt)
                index += 1
                return ('WHILE', condition, body), index
        elif token_type == 'INPUT':
            index += 1
            var_type = tokens[index][1]
            index += 1
            var_name = tokens[index][1]
            index += 1
            if tokens[index][0] == 'SEMICOLON':
                return ('INPUT', var_type, var_name), index + 1
        elif token_type == 'FUNCTION':
            index += 1
            func_name = tokens[index][1]
            index += 1
            if tokens[index][0] == 'LPAREN':
                index += 1
                func_args = []
                while tokens[index][0] != 'RPAREN':
                    func_args.append(tokens[index][1])
                    index += 1
                    if tokens[index][0] == 'COMMA':
                        index += 1
                index += 1
                if tokens[index][0] == 'LBRACE':
                    index += 1
                    func_body = []
                    while tokens[index][0] != 'RBRACE':
                        stmt, index = parse_statement(index)
                        func_body.append(stmt)
                    index += 1
                    return ('FUNCTION', [func_name] + func_args, func_body), index
        raise SyntaxError(f"Invalid statement on line {line_number}")



    while index < len(tokens):
        node, index = parse_statement(index)
        ast.append(node)
    return ast


def evaluate_condition(condition, variables):
    left_expr, op, right_expr = condition[1], condition[2], condition[3]
    left_value = variables.get(left_expr, left_expr) if isinstance(left_expr, str) else left_expr
    right_value = variables.get(right_expr, right_expr) if isinstance(right_expr, str) else right_expr
    
    # Convert string representations of numbers to integers if needed
    if isinstance(left_value, str) and left_value.isdigit():
        left_value = int(left_value)
    if isinstance(right_value, str) and right_value.isdigit():
        right_value = int(right_value)
    
    if op == '==':
        return left_value == right_value
    elif op == '!=':
        return left_value != right_value
    elif op == '<':
        return left_value < right_value
    elif op == '>':
        return left_value > right_value
    elif op == '<=':
        return left_value <= right_value
    elif op == '>=':
        return left_value >= right_value
    raise SyntaxError("Invalid operator in condition")

def interpret_node(node, variables, functions):
    if node[0] == 'PRINT':
        expr = node[1]
        if isinstance(expr, str) and expr in variables:
            print(variables[expr])
        else:
            print(expr[1:-1] if expr.startswith('"') else expr)
    elif node[0] == 'ASSIGN':
        var_name = node[1]
        expr = node[2]
        if isinstance(expr, tuple) and expr[0] == 'BINARY_OP':
            left_expr = variables.get(expr[1], expr[1])
            right_expr = variables.get(expr[3], expr[3])
            if expr[2] == 'PLUS':
                variables[var_name] = left_expr + right_expr
            elif expr[2] == 'MINUS':
                variables[var_name] = left_expr - right_expr
            elif expr[2] == 'MULTIPLY':
                variables[var_name] = left_expr * right_expr
            elif expr[2] == 'DIVIDE':
                variables[var_name] = left_expr / right_expr
            elif expr[2] == 'MODULO':
                variables[var_name] = left_expr % right_expr
        elif isinstance(expr, str) and expr in variables:
            variables[var_name] = variables[expr]
        else:
            variables[var_name] = expr
    elif node[0] == 'IF':
        condition = node[1]
        if_body = node[2]
        else_body = node[3]
        if evaluate_condition(condition, variables):
            result = interpret(if_body, variables, functions)
            if result is not None:
                return result
        else:
            result = interpret(else_body, variables, functions)
            if result is not None:
                return result
    elif node[0] == 'WHILE':
        condition = node[1]
        body = node[2]
        while evaluate_condition(condition, variables):
            result = interpret(body, variables, functions)
            if result is not None:
                return result
    elif node[0] == 'INPUT':
        var_type = node[1]
        var_name = node[2]
        user_input = input()
        if var_type == 'int':
            variables[var_name] = int(user_input)
        elif var_type == 'string':
            variables[var_name] = user_input
        else:
            raise SyntaxError(f"Unsupported input type: {var_type}")
    elif node[0] == 'INCREMENT':
        var_name = node[1]
        if var_name in variables:
            variables[var_name] += 1
        else:
            raise NameError(f"Variable '{var_name}' not defined")
    elif node[0] == 'DECREMENT':
        var_name = node[1]
        if var_name in variables:
            variables[var_name] -= 1
        else:
            raise NameError(f"Variable '{var_name}' not defined")
    elif node[0] == 'FUNCTION':
        func_name = node[1][0]
        func_args = node[1][1:]
        func_body = node[2]
        functions[func_name] = (func_args, func_body)
    elif node[0] == 'CALL':
        func_name = node[1]
        call_args = node[2]
        if func_name in functions:
            func_args, func_body = functions[func_name]
            local_vars = variables.copy()
            for arg_name, arg_value in zip(func_args, call_args):
                local_vars[arg_name] = variables.get(arg_value, arg_value)
            result = interpret(func_body, local_vars, functions)
            if result is not None:
                return result
        else:
            raise NameError(f"Function '{func_name}' not defined")
def interpret(ast, variables, functions):
    for node in ast:
        result = interpret_node(node, variables, functions)
        if result is not None:
            return result


def interpret(ast, variables, functions):
    for node in ast:
        interpret_node(node, variables, functions)

def main():
    if len(sys.argv) != 2:
        print("Usage: python my_language.py <filename>")
        return
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as file:
            program = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    
    tokens = tokenize(program)
    ast = parse(tokens)
    variables = {}
    functions = {}
    interpret(ast, variables, functions)

if __name__ == "__main__":
    main()
