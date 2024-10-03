import re

# Lexer (updated to include EXPYTH token)
def lexer(code):
    tokens = []
    token_specification = [
        ('PRINTLN', r'!println'),
        ('PRINT',   r'!print'),
        ('EXPYTH',  r'!expyth'),  # Added EXPYTH token
        ('VAR',     r'var'),
        ('IF',      r'if'),
        ('TRUE',    r'True'),
        ('FALSE',   r'False'),
        ('ID',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUMBER',  r'\d+(\.\d*)?'),
        ('STRING',  r'"[^"]*"'),
        ('NEQ',     r'!='),
        ('EQ',      r'=='),
        ('ASSIGN',  r'='),
        ('LPAREN',  r'\('),
        ('RPAREN',  r'\)'),
        ('LBRACE',  r'\{'),
        ('RBRACE',  r'\}'),
        ('GT',      r'>'),
        ('LT',      r'<'),
        ('NEWLINE', r'\n'),
        ('COMMENT', r'#.*'),
        ('SKIP',    r'[ \t]+'),
        ('MISMATCH',r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'TRUE':
            value = True
        elif kind == 'FALSE':
            value = False
        elif kind in ['SKIP', 'COMMENT']:
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
        tokens.append((kind, value))
    return tokens

# Parser (updated to handle EXPYTH statements)
def parser(tokens):
    def parse_block():
        block = []
        while i < len(tokens) and tokens[i][0] != 'RBRACE':
            stmt = parse_statement()
            if stmt:
                block.append(stmt)
        return block

    def parse_statement():
        nonlocal i
        print(f"Parsing token {i}: {tokens[i]}")  # Debug print
        if tokens[i][0] in ['PRINT', 'PRINTLN']:
            if i+3 < len(tokens) and tokens[i+1][0] == 'LPAREN' and tokens[i+2][0] in ['STRING', 'ID', 'TRUE', 'FALSE', 'NUMBER'] and tokens[i+3][0] == 'RPAREN':
                stmt = (tokens[i][0], tokens[i+2])
                i += 4
                return stmt
            else:
                raise SyntaxError(f'Invalid print statement at token {i}: {tokens[i:i+4]}')
        elif tokens[i][0] == 'EXPYTH':
            if i+3 < len(tokens) and tokens[i+1][0] == 'LPAREN' and tokens[i+2][0] == 'STRING' and tokens[i+3][0] == 'RPAREN':
                stmt = ('EXPYTH', tokens[i+2])
                i += 4
                return stmt
            else:
                raise SyntaxError(f'Invalid expyth statement at token {i}: {tokens[i:i+4]}')
        elif tokens[i][0] == 'VAR':
            if i+3 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+2][0] == 'ASSIGN' and tokens[i+3][0] in ['STRING', 'NUMBER', 'ID', 'TRUE', 'FALSE']:
                stmt = ('VAR', tokens[i+1][1], tokens[i+3])
                i += 4
                return stmt
            else:
                raise SyntaxError(f'Invalid variable declaration at token {i}: {tokens[i:i+4]}')
        elif tokens[i][0] == 'IF':
            print(f"Parsing IF statement at token {i}")  # Debug print
            if i+6 < len(tokens):
                print(f"Tokens for IF: {tokens[i:i+7]}")  # Debug print
                if tokens[i+1][0] == 'LPAREN' and tokens[i+3][0] in ['EQ', 'NEQ', 'GT', 'LT'] and tokens[i+5][0] == 'RPAREN' and tokens[i+6][0] == 'LBRACE':
                    condition = (tokens[i+3][0], tokens[i+2], tokens[i+4])
                    i += 7  # Move past the '{'
                    block = parse_block()
                    if i < len(tokens) and tokens[i][0] == 'RBRACE':
                        i += 1  # Move past the '}'
                    else:
                        raise SyntaxError(f'Missing closing brace for if statement at token {i}')
                    return ('IF', condition, block)
                elif tokens[i+1][0] == 'LPAREN' and tokens[i+2][0] in ['TRUE', 'FALSE', 'ID'] and tokens[i+3][0] == 'RPAREN' and tokens[i+4][0] == 'LBRACE':
                    condition = tokens[i+2]
                    i += 5  # Move past the '{'
                    block = parse_block()
                    if i < len(tokens) and tokens[i][0] == 'RBRACE':
                        i += 1  # Move past the '}'
                    else:
                        raise SyntaxError(f'Missing closing brace for if statement at token {i}')
                    return ('IF', condition, block)
            raise SyntaxError(f'Invalid if statement at token {i}: {tokens[i:i+7]}')
        elif tokens[i][0] == 'NEWLINE':
            i += 1
            return None
        else:
            raise SyntaxError(f'Unexpected token: {tokens[i]}')

    statements = []
    i = 0
    while i < len(tokens):
        stmt = parse_statement()
        if stmt:
            statements.append(stmt)
    return statements

# Code generator (updated to handle EXPYTH statements)
def generate_code(ast):
    def generate_condition(cond):
        if isinstance(cond, tuple) and len(cond) == 3:
            op, left, right = cond
            op_map = {'EQ': '==', 'NEQ': '!=', 'GT': '>', 'LT': '<'}
            return f"{generate_value(left)} {op_map[op]} {generate_value(right)}"
        else:
            return generate_value(cond)

    def generate_value(val):
        if val[0] == 'STRING':
            return val[1]  # Return the string as-is, including the quotes
        elif val[0] in ['NUMBER', 'TRUE', 'FALSE']:
            return str(val[1])
        elif val[0] == 'ID':
            return val[1]
        else:
            raise ValueError(f"Unexpected value type: {val[0]}")

    def generate_block(block, indent_level):
        indent = "    " * indent_level
        return "\n".join(indent + generate_statement(stmt, indent_level) for stmt in block)

    def generate_statement(stmt, indent_level):
        if stmt[0] == 'PRINTLN':
            return f"print({generate_value(stmt[1])})"
        elif stmt[0] == 'PRINT':
            return f"print({generate_value(stmt[1])}, end='')"
        elif stmt[0] == 'EXPYTH':
            return f"exec({generate_value(stmt[1])})"
        elif stmt[0] == 'VAR':
            return f"{stmt[1]} = {generate_value(stmt[2])}"
        elif stmt[0] == 'IF':
            condition = generate_condition(stmt[1])
            block = generate_block(stmt[2], indent_level + 1)
            return f"if {condition}:\n{block}"

    return "\n".join(generate_statement(stmt, 0) for stmt in ast)

# Main compiler function (unchanged)
def compile(code):
    try:
        tokens = lexer(code)
        print("Tokens:", tokens)  # Debug print
        ast = parser(tokens)
        print("AST:", ast)  # Debug print
        return generate_code(ast)
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        return None

# Read from test.upl file (unchanged)
def read_test_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except IOError:
        print(f"Error: There was an issue reading the file '{filename}'.")
        return None

# Main execution (unchanged)
if __name__ == "__main__":
    test_filename = 'test.upl'
    test_code = read_test_file(test_filename)
    
    if test_code is not None:
        print("Original code:")
        print(test_code)
        
        compiled_code = compile(test_code)
        if compiled_code:
            print("\nCompiled code:")
            print(compiled_code)
            
            print("\nExecuting compiled code:")
            exec(compiled_code)
        else:
            print("Compilation failed.")
    else:
        print("Compilation aborted due to file reading error.")