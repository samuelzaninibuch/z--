import re
import sys

# Define token types
TOKEN = [
    ('STRING', r'\".*\"'),
    ('PRINT', r'print'),
    ('SEMICOLON', r';'),
    ('EQUALS', r'='),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('INPUT', r'input'),
    ('INCREMENT', r'\+\+'),
    ('DECREMENT', r'--'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
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

debug_mode = False  # Set this to True to enable debug prints

def tokenize(program):
    tokens = []
    for line in program:
        while line:
            match = None
            for token_type, pattern in TOKEN:
                regex = re.compile(pattern)
                match = regex.match(line)
                if match:
                    tokens.append((token_type, match.group(0)))
                    line = line[match.end():].strip()
                    break
            if not match:
                raise SyntaxError(f'Unexpected character: {line[0]}')
    if debug_mode:
        print("Tokens:", tokens) 
    return tokens

def parse(tokens):
    def parse_expression(index):
        token_type, token_value = tokens[index]
        if token_type == 'STRING':
            return token_value, index + 1
        elif token_type == 'NUMBER':
            return int(token_value), index + 1
        elif token_type == 'IDENTIFIER':
            return token_value, index + 1
        raise SyntaxError("Invalid expression")

    def parse_condition(index):
        if tokens[index][0] == 'LPAREN':
            index += 1
            left_expr, index = parse_expression(index)
            op = tokens[index][1]
            index += 1
            right_expr, index = parse_expression(index)
            if tokens[index][0] == 'RPAREN':
                return ('CONDITION', left_expr, op, right_expr), index + 1
        raise SyntaxError("Invalid condition")

    def parse_statement(index):
        token_type, token_value = tokens[index]
        if debug_mode:
            print(f"Parsing statement: {token_type}, {token_value}")  # Debug print
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
        raise SyntaxError("Invalid statement")

    ast = []
    index = 0
    while index < len(tokens):
        node, index = parse_statement(index)
        ast.append(node)
        if debug_mode:
            print(f"AST so far: {ast}")  # Debug print
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

def interpret_node(node, variables):
    if node[0] == 'PRINT':
        expr = node[1]
        if isinstance(expr, str) and expr in variables:
            print(variables[expr])
        else:
            print(expr[1:-1] if expr.startswith('"') else expr)
    elif node[0] == 'ASSIGN':
        var_name = node[1]
        expr = node[2]
        if isinstance(expr, str) and expr in variables:
            variables[var_name] = variables[expr]
        else:
            variables[var_name] = expr
    elif node[0] == 'IF':
        condition = node[1]
        if_body = node[2]
        else_body = node[3]
        if evaluate_condition(condition, variables):
            interpret(if_body, variables)
        else:
            interpret(else_body, variables)
    elif node[0] == 'WHILE':
        condition = node[1]
        body = node[2]
        while evaluate_condition(condition, variables):
            interpret(body, variables)
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
        print(f"Decrementing variable: {var_name}")  # Debug print
        if var_name in variables:
            print(f"Current value of {var_name}: {variables[var_name]}")  # Debug print
            variables[var_name] -= 1
            print(f"New value of {var_name}: {variables[var_name]}")  # Debug print
        else:
            raise NameError(f"Variable '{var_name}' not defined")

def interpret(ast, variables):
    for node in ast:
        interpret_node(node, variables)

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
    interpret(ast, variables)

if __name__ == "__main__":
    main()
