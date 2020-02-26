import sys
import getopt


def main():
    """
    This function iterates through a properly formatted
    pseudocode text file and returns (roughly) equivalent
    python code.

    TODO:
    The main() function probably shouldn't be used for
    anything other than opening the file and calling
    a different function to parse through everything.
    """

    filename = "code.txt"
    debug = True

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "f:d", ["file=", "debug"])
    except getopt.GetoptError:
        sys.exit()
    for opt, arg in opts:
        if opt in ("-f", "--file"):
            filename = arg
        if opt in ("-d", "--debug"):
            debug = True
    try:
        with open(filename) as file:
            code = file.read()
        if debug:
            print("----- Pseudocode -----")
            print(code)
            print("----- Ends -----\n")
        # change code to Python
        code = transcode(code)

        if debug:
            print("----- Executed code ------")
            print(code)
            print("----- Ends -----\n")
            print("----- Output -----")
        # execute the newly created Python code
        exec(code)
    except FileNotFoundError:
        print(filename + " not found.")


def get_variable(code, loc):
    temp_var = ""
    while code[loc] not in (" ", ",", "(", ")", ":"):
        temp_var = code[loc] + temp_var
        loc = loc - 1
    return (temp_var, loc)


def update_code(code):
    # Used to handle the SWITCH statement
    switch_var = ""
    default_statement = ""

    # Selects all cases of things with parameters and treats them appropiately
    for i in range(len(code)):
        if code[i:i + 3] == "FOR":
            line = code[i:]
            index = line.index("\n")
            linesplit = line[:index].split()
            variable = linesplit[1]
            start = linesplit[3]
            end = int(linesplit[5]) + 1

            new_line = f"for {variable} in range({start},{end}):"

            code = code[:i] + new_line + code[i + index:]
        elif code[i:i + 5] == "WHILE":
            line = code[i + 5:]
            index = line.index("\n")
            rest = line[:index]

            new_line = f"while {rest}:"

            code = code[:i] + new_line + code[i + 5 + index:]
        elif code[i:i + 6] == "ELSEIF":
            line = code[i + 6:]
            index = line.index("\n")
            rest = line[:index]

            new_line = f"elif {rest}:"

            code = code[:i] + new_line + code[i + 6 + index:]
        elif code[i:i + 4] == "ELSE":
            code = code[:i] + "else:" + code[i + 4:]
        elif code[i:i + 2] == "IF":
            line = code[i + 2:]
            index = line.index("\n")
            rest = line[:index - 4]

            new_line = f"if {rest}:"

            code = code[:i] + new_line + code[i + 2 + index:]
        elif code[i:i + 9] == "ENDSWITCH":
            line = code[i + 9:]
            index = line.index("\n")
            switch_var = ""
            default_statement = ""

            code = code[:i] + code[i + 9 + index:]
        elif code[i:i + 6] == "SWITCH":
            line = code[i + 7:]
            index = line.index("\n")
            switch_var = line[:index - 1]

            code = code[:i] + code[i + 7 + index:]
        elif code[i:i + 4] == "CASE":
            line = code[i + 4:]
            index = line.index("\n")
            rest = line[:index - 1]

            new_line = f"if {switch_var}=={rest}:"
            default_statement = default_statement + \
                f" {switch_var} != {rest} and "

            code = code[:i] + new_line + code[i + 4 + index:]
        elif code[i:i + 7] == "DEFAULT":
            line = code[i + 7:]
            index = line.index("\n")
            code = code[:i] + "if " + \
                default_statement[:-4] + ":" + code[i + 7 + index:]
        elif code[i:i + 7] == ".LENGTH":
            temp = i - 1
            temp_var = ""

            # Code will be variablename.LENGTH so reverse back until
            # we get to the start of the variable name
            (temp_var, temp) = get_variable(code, temp)

            new_line = f"len({temp_var})"

            code = code[:temp + 1] + new_line + code[i + 7:]
        elif code[i:i + 11] == ".SUBSTRING(":
            temp = i - 1
            temp_var = ""

            # Code will be variablename.SUBSTRING so reverse back until
            # we get to the start of the variable name
            (temp_var, temp) = get_variable(code, temp)

            line = code[i + 11:]
            index = line.index(")")
            rest = line[:index]
            params = rest.split(",")
            start = params[0]
            end = params[1]
            new_line = f"{temp_var}[{start}:{start}+{end}]"

            code = code[:temp + 1] + new_line + code[i + 11 + index + 1:]
        elif code[i:i + 3] == "STR":
            code = code[:i] + "str" + code[i + 3:]
        elif code[i:i + 8] == "FUNCTION":
            line = code[i + 8:]
            index = line.index("\n")
            rest = line[:index]

            new_line = f"def {rest}:"

            code = code[:i] + new_line + code[i + 8 + index:]
        elif code[i:i + 9] == "PROCEDURE":
            line = code[i + 9:]
            index = line.index("\n")
            rest = line[:index]

            new_line = f"def {rest}:"

            code = code[:i] + new_line + code[i + 9 + index:]
        elif code[i:i + 5] == "ARRAY":
            line = code[i + 6:]
            index = line.index("\n")
            rest = line[:index]
            params = rest.split("[")
            var_name = params[0]
            size = params[1][:-1]

            new_line = f"{var_name} = [None] * {size}"

            code = code[:i] + new_line + code[i + 6 + index:]
        elif code[i:i + 6] == "APPEND":
            params_s = code[i:]
            index = params_s.index("\n")
            params_s = params_s[params_s.index("(") + 1:index - 1]

            params = find_params(params_s)
            append_py = f"{params[0]}.append({params[1]})"

            code = code[:i] + append_py + code[i + index:]
        elif code[i:i + 6] == "REMOVE":
            params_s = code[i:]
            index = params_s.index("\n")
            params_s = params_s[params_s.index("(") + 1:index - 1]

            params = find_params(params_s)
            remove_py = f"del {params[0]}[{params[1]}]"

            code = code[:i] + remove_py + code[i + index:]
        elif code[i:i + 6] == "INSERT":
            params_s = code[i:]
            index = params_s.index("\n")
            params_s = params_s[params_s.index("(") + 1:index - 1]

            params = find_params(params_s)
            insert_py = f"{params[0]}.insert({params[1]}, {params[2]})"

            code = code[:i] + insert_py + code[i + index:]
    return code


def transcode(code):
    # Imports random if random is used
    if "RANDOM" in code:
        code = "import random\n" + code
    # Dict of pseudocode keywords/syntax and their python equivalents
    replacements = {
        " = ": " = ",
        " == ": " == ",
        "PRINT": "print",
        " AND ": " and ",
        " OR ": " or ",
        "NOT": "not",
        "MOD": "%",
        "DIV": "//",
        "INT": "int",
        "FLOAT": "float",
        " IN ": " in ",
        "RETURN": "return",
        "RANDOM": "random.randint",
        "ENDIF": "",
        "INPUT": "input",
    }

    # Replaces everything in the pseudocode with python equivalents
    equals_replaced = False
    for r in replacements:
        if not (r == " = " and equals_replaced):
            code = code.replace(r, replacements[r])
        if r == " = ":
            equals_replaced = True
    """
    update_code(code) dynamically changes the string 'code'.  This means that
    the len(code) in the for loop can be incorrect and so the whole of code
    may not be searched in one operation.  Therefore we call
    update_code(code) until no changes have been made - this means that we
    are done
    """
    new_code = ""
    changed = True
    while changed:
        new_code = update_code(code)
        if new_code == code:
            changed = False
        code = new_code
    return code


def find_params(s):
    """
    Takes a section of pseudocode that is being passed to something as
    a parameter or set of parameters and parses them out individually
    """
    params = []

    ignore = False
    i = 0
    while i < len(s):
        if s[i] == "(":
            ignore = True
        elif s[i] == ")":
            ignore = False
        if ("," not in s and len(s) > 0) or (i == len(s) - 1 and len(s) > 0):
            params.append(s)
            break
        if s[i] == "," and not ignore:
            params.append(s[:i].strip())
            s = s[i + 1:]
            i = -1
        i += 1
    return params


if __name__ == "__main__":
    main()
