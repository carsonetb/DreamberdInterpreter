import sys
from word2number import w2n

filepath = "test.db"
file = open(filepath, "r")
text = file.readlines()
variables = {}
functions = {}
stack = []

currency_list = ["؋", "฿", "₵", "¢", "₡", "$", "₫", "đ", "Đ", "֏", "Ξ", "€", "ƒ", "F", "G", "₲", "h", "₴", "₭", "₾", "₺", "₼", "₦", "£", "P", 
                  "Q", "q", "R", "﷼", "៛", "₽", "ރ", "₹", "₪", "⃀", "৳", "₸", "₮", "₩", "¥", "రూ", "௹", "૱", "ರ", "රු", "꠸", "𞋿", "₳", "₰",
                  "₻", "₯", "₠", "ƒ", "₤", "ℳ︁", "₡", "₷", "৲", "৹", "৻", "߾", "߿"]

class Bool:
    def __init__(self, true, false, maybe):
        self.true = true
        self.false = false
        self.maybe = maybe
    
    def from_bool(a):
        if a:
            return Bool(True, False, False)
        elif not a:
            return Bool(False, True, False)
        else:
            return Bool(False, False, True)
    
    def __str__(self):
        if self.true:
            return "true"
        if self.false:
            return "false"
        if self.maybe:
            return "maybe"

class Class:
    def __init__(self):
        self.functions = {}
        self.variables = {}
        self.instantiated = False

class ClassInstance:
    def __init__(self, functions, variables):
        self.functions = functions
        self.variables = variables

def call_func(line: str, line_num: int, return_var=None, custom_variables={}, custom_functions={}):
    line = line.strip(" ")
    operation = "idk"
    disabled = False

    if not custom_variables:
        custom_variables = variables
    if not custom_functions:
        custom_functions = functions

    for character in line:
        if disabled and not character == "]":
            continue
        else:
            disabled = False

        if character == "[":
            disabled = True
        if character == ".":
            operation = "on"
            break
        if character == "(":
            operation = "call"
    
    if operation == "on":
        func_info = parse_function_call(line)
        var_info = custom_variables[func_info["on"]]
        
        if debug:
            print(f"DEBUG: Attempting to call {func_info} on variable {var_info}")
        
        if var_info["dectype"] == "ci":
            caller = custom_variables[func_info["on"]]["val"]
            return call_func(line.partition(".")[2], line_num, return_var, caller.variables, caller.functions)

        if var_info["vartype"] == str:
            if func_info["name"] == "pop":
                var_info["val"] = var_info["val"][:-1]
            if func_info["name"] == "push":
                var_info["val"] += parse_var(func_info["args"][0])
    
    if operation == "call":
        info = parse_function_call(line)
        info.pop("on")
        info["from"] = line_num
        info["stacktype"] = "call_func"
        info["return_to"] = return_var

        ind = 0
        for arg in info["args"]:
            variable = parse_var(arg)
            custom_variables[custom_functions[info["name"]]["args"][ind].strip(" ")] = {
                "dectype": "vv",
                "vartype": type(variable),
                "val": variable,
                "delete_at": custom_functions[info["name"]]["end_line"] + 1,
            }
            ind += 1
        
        stack.append(info)

        if debug:
            print(f"DEBUG: Called function, printing stack. {stack}")
        
        return custom_functions[info["name"]]["line"]
        
def conv_correct_class(var):
    if var == True:
        return Bool(True, False, False)
    if var == False:
        return Bool(False, True, False)
    return var

def is_function(on: str):
    biggest = "function"
    ind = 0
    for char in on:
        while char != biggest[ind]:
            ind += 1
            if ind > 7:
                return False
    
    return True    

# Thanks chatgpt
def is_word_number(input_string: str):
    input_string.replace(" ", "-")
    try:
        # Try converting the input string to a number
        number = w2n.word_to_num(input_string)
        return True
    except ValueError:
        # If conversion fails, it's not a valid number in words
        return False 

def parse_var(var: str, custom_variables=None):
    var = var.strip(" ")

    if not custom_variables:
        custom_variables = variables

    if str(var) in deleted_keywords:
        print(f"ERROR: Deleted {var}!")
        quit()

    if custom_variables.get(var):
        if str(var) in deleted_keywords:
            print(f"ERROR: Deleted {var}!")
            quit()
        return custom_variables.get(var)["val"]
    
    if var.find("====") != -1:
        var = var.split("====")
        var = var[0].strip(" ") == var[1].strip(" ") # Funny trick ... same name? same variable.
        if str(var) in deleted_keywords:
            print(f"ERROR: Deleted {var}!")
            quit()
        return Bool.from_bool(var)

    if var.find("===") != -1:
        var = var.split("===")
        var = parse_var(var[0]) == parse_var(var[1])
        if str(var) in deleted_keywords:
            print(f"ERROR: Deleted {var}!")
            quit()
        return Bool.from_bool(var)

    if var.find("==") != -1:
        var = var.split("==")
        l = parse_var(var[0])
        r = parse_var(var[1])
        if l == r:
            if "true" in deleted_keywords:
                print(f"ERROR: Deleted true!")
                quit()
            return True
        elif type(l) == str:
            return Bool.from_bool(str(r) == l)
        elif type(r) == str:
            return Bool.from_bool(r == str(l))
    
    if var.find("=") != -1:
        var = var.split("=")
        l = parse_var(var[0])
        r = parse_var(var[1])
        if l == r:
            if "true" in deleted_keywords:
                print(f"ERROR: Deleted true!")
                quit()
            return Bool(True, False, False)
        elif type(l) == str:
            if str(Bool.from_bool(str(r) == l))in deleted_keywords:
                print(f"ERROR: Deleted {str(Bool.from_bool(str(r) == l))}!")
                quit()
            return Bool.from_bool(str(r) == l)
        elif type(r) == str:
            if str(Bool.from_bool(r == str(l)))in deleted_keywords:
                print(f"ERROR: Deleted {str(Bool.from_bool(r == str(l)))}!")
                quit()
            return Bool.from_bool(r == str(l))
        elif (type(l) == float or type(l) == int or l.lstrip("-").split(".")[0].isnumeric()) and (type(r) == float or type(r) == int or r.lstrip("-").split(".")[0].isnumeric()):
            if str(Bool.from_bool(round(float(l)) == round(float(r)))) in deleted_keywords:
                print(f"ERROR: Deleted {str(Bool.from_bool(round(float(l)) == round(float(r))))}!")
                quit()
            return Bool.from_bool(round(float(l)) == round(float(r)))
    
    operators = []
    ind = 0
    lowest_sig = 99999
    highest_sig = -99999
    for char in var:
        if char == "+" or char == "-" or char == "*" or char == "/" or char == "^":
            sig = -(len(var[:ind]) - len(var[:ind].rstrip(" ")))
            operators.append({
                "ind": ind,
                "operator": char,
                "significance": sig,
                "op_significance": 0,
                "index": ind
            })
            if sig < lowest_sig:
                lowest_sig = sig
            if sig > highest_sig:
                highest_sig = sig

        if char == "*" or char == "/":
            operators[-1]["op_significance"] = 1
        
        if char == "^":
            operators[-1]["op_significance"] = 2
        
        ind += 1
    
    # Totally readable code
    if operators:
        sorted_sig = [[] for _ in range(highest_sig - lowest_sig + 1)]
        for operator in operators:
            sorted_sig[operator["significance"] - lowest_sig].append(operator)
        sorted_op_sig = [[[], [], []] for _ in range(highest_sig - lowest_sig + 1)]
        for i in range(len(sorted_sig)):
            for operator in sorted_sig[i]:
                sorted_op_sig[i][operator["op_significance"]].append(operator)
    
        to_split = sorted_op_sig[0][0][0] if len(sorted_op_sig[0][0]) > 0 else (sorted_op_sig[0][1][0] if len(sorted_op_sig[0][1]) > 0 else sorted_op_sig[0][2][0])

        if to_split["operator"] == "+":
            var = parse_var(var[:to_split["ind"]]) + parse_var(var[to_split["ind"] + 1:])
            if str(var) in deleted_keywords:
                print(f"ERROR: Deleted {var}!")
                quit()
            return var
        
        if to_split["operator"] == "-":
            var = parse_var(var[:to_split["ind"]]) - parse_var(var[to_split["ind"] + 1:])
            if str(var) in deleted_keywords:
                print(f"ERROR: Deleted {var}!")
                quit()
            return var
        
        if to_split["operator"] == "*":
            var = parse_var(var[:to_split["ind"]]) * parse_var(var[to_split["ind"] + 1:])
            if str(var) in deleted_keywords:
                print(f"ERROR: Deleted {var}!")
                quit()
            return var
        
        if to_split["operator"] == "/":
            var = parse_var(var[:to_split["ind"]]) / parse_var(var[to_split["ind"] + 1:])
            if str(var) in deleted_keywords:
                print(f"ERROR: Deleted {var}!")
                quit()
            return var

        if var.find("^") != -1:
            var = parse_var(var[:to_split["ind"]]) ** parse_var(var[to_split["ind"] + 1:])
            if str(var) in deleted_keywords:
                print(f"ERROR: Deleted {var}!")
                quit()
            return var

    if var.startswith('"') or var.startswith("'"):
        while var.startswith('"') or var.startswith("'"):
            var = var.strip('"')
            var = var.strip("'")
        
        while var.find("{") != -1:
            contained_var = var.split("{")[1].split("}")[0]
            val = parse_var(contained_var)

            currency = var.split("{")[0][-1]
            if not currency in currency_list:
                print(f"ERROR: Line (I don't know the line), I don't know about that currency.")
                quit()
        
        if str(var) in deleted_keywords:
            print(f"ERROR: Deleted {var}!")
            quit()
        return var

    if var.lstrip("-").split(".")[0].isnumeric():
        if str(float(var)) in deleted_keywords:
            print(f"ERROR: Deleted {float(var)}!")
            quit()
        return float(var)
    
    if is_word_number(var):
        if str(w2n.word_to_num(var)) in deleted_keywords:
            print(f"ERROR: Deleted {w2n.word_to_num(var)}!")
            quit()
        return w2n.word_to_num(var)
    
    if var.find(".") != -1:
        return parse_var(var.partition(".")[0]).variables[parse_var(var.partition(".")[2])]["val"]
    
    if var.startswith("["):
        var = var.removeprefix("[")
        var = var.removesuffix("]")
        if var.find("[") != -1:
            print("ERROR: Don't have arrays in arrays right now.")
        var = var.split(",")
        final = {}
        index = -1
        for item in var:
            final[index] = parse_var(item)
            index += 1
        if str(final) in deleted_keywords:
            print(f"ERROR: Deleted {final}!")
            quit()
        return final
    elif var.endswith("]"):
        index = parse_var(var.split("[")[1].removesuffix("]"))
        var = custom_variables[var.split("[")[0]]["val"][index]
        if str(var) in deleted_keywords:
            print(f"ERROR: Deleted {var}!")
            quit()
        return var
    
    if var == "true":
        return Bool(True, False, False)
    if var == "false":
        if "false" in deleted_keywords:
            print("ERROR: Deleted false!")
            quit()
        return Bool(False, True, False)
    if var == "maybe":
        if "true" in deleted_keywords:
            print("ERROR: Deleted true!")
            quit()
        return Bool(False, False, True)
    
    # It's probably a string.
    if str(var) in deleted_keywords:
        print(f"ERROR: Deleted {var}!")
        quit()

    return var

def parse_function_call(line: str):
    func = line.split("(")[0].split(".")
    if len(func) > 1:
        name = func[1]
        on = func[0]
    else:
        name = line.split("(")[0]
        on = ""
    
    args = line.removeprefix(line.split("(")[0] + "(").rpartition(")")[0].split(",")
    if args == [""]:
        args = []
    
    return {
        "name": name,
        "on": on,
        "args": args
    }

line_num = 0
num_open_curl_bracket = 0
stepping_through_function = False
function_stepping_through = {}
class_stepping_through = None
called_one_liner = False
base_spaces = 0
negative_spaces = False
global deleted_keywords
deleted_keywords = []
when_checks = []

while line_num < len(text):
    indent_num = 0
    line: str = text[line_num]
    line_num += 1

    if stepping_through_function:
        num_open_curl_bracket += line.count("{")
        num_open_curl_bracket -= line.count("}")

        if num_open_curl_bracket == 0:
            if function_stepping_through != "when":
                function_stepping_through["end_line"] = line_num - 1
            stepping_through_function = False
        
        continue

    redo_that = True
    while redo_that:
        redo_that = False
        for var_key in variables.keys():
            if variables[var_key]["delete_at"] == line_num:
                variables.pop(var_key)
                redo_that = True
                break

    if line.endswith("\n"):
        line = line.removesuffix("\n")

    debug = line.endswith("?")

    indent_num = 0

    if line.startswith(" "):
        indent_num = len(line) - len(line.lstrip(" "))

        if line_num == 1:
            base_spaces += 1
            negative_spaces = True

    # Remove annoying !s and ?s
    while line.endswith("?") or line.endswith("!") or line.startswith(" ") or line.endswith(" "):
        line = line.removesuffix("?")
        line = line.removesuffix("!")
        line = line.strip(" ")
    
    if line == "":
        continue

    for check in when_checks:
        check_line = text[check - 1]
        print(check_line)
        print(check_line.split("(")[1].split(")")[0])
        if parse_var(check_line.split("(")[1].split(")")[0]) == Bool(True, False, False):
            stack.append({"name": "check_when", "args": [], "from": line_num, "stack_type": "run_when"})

    if line.startswith("}"):
        line_num = stack[-1]["from"] if stack[-1].get("from") else line_num
        stack.pop()
        continue

    if line.startswith("return"):
        if not stack[-1].get("return_to"):
            continue

        variable = parse_var(line.split(" ")[1])
        variables[stack[-1]["return_to"]]["val"] = variable
        variables[stack[-1]["return_to"]]["dectype"] = type(variable)
        line_num = stack[-1]["from"]
        stack.pop()
        continue

    if ((base_spaces - indent_num) if negative_spaces else (indent_num)) % 3 != 0:
        print(f"ERROR: Line {line_num}, incorrect indentation.")
        break

    if line.startswith("delete"):
        if "delete" in deleted_keywords:
            print("ERROR: Deleted delete!")
            break
        
        deleted_keywords.append(line.split(" ")[-1])
        continue

    if line.startswith("print"):
        if "print" in deleted_keywords:
            print("ERROR: Deleted print!")
            break

        args = parse_function_call(line)["args"]
        for var in args:
            val = parse_var(var)
            if type(val) == dict:
                print("[", end = "")
                ind = 1
                for i in sorted(val.keys()):
                    print(val[i], end="")
                    if ind < len(val.keys()):
                        print(",", end=" ")
                    ind += 1
                print("]")
            else:
                print(val)
        continue

    if line.startswith("class"):
        variables[line.split(" ")[1]] = {
            "dectype": "c",
            "vartype": Class,
            "val": Class(),
            "delete_at": 999999,
        }
        stack.append({
            "name": line.split(" ")[1],
            "line": line_num,
            "stacktype": "parse_class"
        })

        if debug:
            print(f"DEBUG: Created a class, {variables[line.split(" ")[1]]}, added parse_class call to stack: {stack[-1]}")

    if line.startswith("when"):
        when_checks.append(line_num)
        stack.append({
            "name": "when_" + str(line_num),
            "line": line_num,
            "stacktype": "parse_when"
        })
        when_checks.append(line_num)

        num_open_curl_bracket += 1
        stepping_through_function = True
        function_stepping_through = "when"
        continue
    
    if is_function(line.split(" ")[0]):
        if line.split(" ")[0] in deleted_keywords:
            print("ERROR: Deleted function!")
            break

        info = parse_function_call(line.partition(" ")[2].split("=>")[0])
        info["line"] = line_num
        info["created_within"] = stack[-1] if len(stack) > 0 else "main"
        info.pop("on")
        if len(stack) == 0:
            functions[info["name"]] = info
        elif stack[-1]["stacktype"] == "parse_class":
            parse_var(stack[-1]["name"]).functions[info["name"]] = info
        else:
            print("Functions inside functions aren't supported yet.")
        info.pop("name")

        if debug:
            print(f"DEBUG: Create function {info}")
    
        num_open_curl_bracket += 1
        stepping_through_function = True
        function_stepping_through = info
        
        if line.find("{") == -1:
            after = line.split("=>")[-1]
            line = line.removesuffix(after)
            text.insert(line_num, after)
            text.insert(line_num + 1, "}")
    
    elif line.startswith("const") or line.startswith("var"):
        if "const" in deleted_keywords and line.startswith("const"):
            print("ERROR: Deleted const!")
            break
        if "var" in deleted_keywords and line.startswith("var"):
            print("ERROR: Deleted var!")
            break
        
        split_spaces = line.split(" ")
        call = False

        
        if line.split("=")[1].strip(" ").startswith("new"):
            variable = parse_var(line.split("=")[1].split("(")[0].strip(" ").removeprefix("new"))
            if variable.instantiated:
                print(f"ERROR: Line {line_num}, class is already instantaited.")
            variable.instantiated = True
            variable = ClassInstance(variable.functions, variable.variables)
            dectype = "ci"
        elif line.split("=")[1].find("(") != -1:
            call = True
            variable = ""
            dectype = "cc"
        else:
            variable = parse_var(line.split("=")[1])

            dectype = "vv"
            if split_spaces[0] == "const" and split_spaces[1] == "const":
                dectype = "cc"
            if split_spaces[0] == "var" and split_spaces[1] == "const":
                dectype = "vc"
            if split_spaces[0] == "const" and split_spaces[1] == "var":
                dectype = "cv"
        
        # Having a file longer than this would be crazy.
        lifetime = 99999

        if split_spaces[2].find("<") != -1:
            val = split_spaces[2].split("<")[1].strip(" ").removesuffix(">")
            if val == "Infinity":
                print("No way am i making a saving system yet.")
            if val.endswith("s"):
                print("I ain't making seconds yet.")
            else:
                lifetime = parse_var(val)

        new_var = {
            "dectype": dectype,
            "vartype": type(variable),
            "val": variable,
            "delete_at": line_num + lifetime,
        }

        if len(stack) == 0 or stack[-1]["stacktype"] != "parse_class":
            variables[split_spaces[2]] = new_var
        else:
            parse_var(stack[-1]["name"]).variables[split_spaces[2]] = new_var

        if call:
            if debug:
                print(f"DEBUG: Line {line_num}, created variable {split_spaces[2]} as output of function {line.split("=")[1]}")
            line_num = call_func(line.split("=")[1], line_num, split_spaces[2])
            continue

        if debug:
            print(f"DEBUG: Line {line_num}, created variable {split_spaces[2]}. Info: {new_var}")

    else:
        operation = "idk"
        disabled = False
        for character in line:
            if disabled and not character == "]":
                continue
            else:
                disabled = False

            if character == "[":
                disabled = True
            if character == ".":
                operation = "on"
                break
            if character == "=":
                operation = "assign"
                break
            if character == "(":
                operation = "call"
        
        if operation == "idk":
            continue
        
        if operation == "on":
            func_info = parse_function_call(line)
            var_info = variables[func_info["on"]]
            
            if debug:
                print(f"DEBUG: Attempting to call {func_info} on variable {var_info}")

            if var_info["dectype"] == "cc" or var_info["dectype"] == "vc":
                print(f"ERROR: On line {line_num} Can't call functions on this variable!")
                break
            
            if var_info["dectype"] == "ci":
                func_info["from"] = line_num
                func_info["stacktype"] = "call_func"

                ind = 0
                for arg in info["args"]:
                    variable = parse_var(arg)
                    variables[func_info["on"]]["val"].variables[variables[func_info["on"]]["val"].functions[info["name"]]["args"][ind].strip(" ")] = {
                        "dectype": "vv",
                        "vartype": type(variable),
                        "val": variable,
                        "delete_at": variables[func_info["on"]]["val"].functions[info["name"]]["end_line"] + 1,
                    }
                    ind += 1
                
                stack.append(func_info)

                if debug:
                    print(f"DEBUG: Called function, printing stack. {stack}")
                
                line_num = variables[func_info["on"]]["val"].functions[func_info["name"]]["line"]

            if var_info["vartype"] == str:
                if func_info["name"] == "pop":
                    var_info["val"] = var_info["val"][:-1]
                if func_info["name"] == "push":
                    var_info["val"] += parse_var(func_info["args"][0])
        
        if operation == "assign":
            split = line.split("=")

            if split[0].find(".") != -1:
                split_call = split[0].split(".")
                split = split_call[1]
            else:
                split_call = None

            if split[1].find("(") != -1:
                line_num = call_func(split[1], line_num, split[0])
                continue

            if split[0].find("[") != -1:
                (parse_var(split_call[0]).variables if split_call else variables)[split[0].split("[")[0].strip(" ")]["val"][parse_var(split[0].split("[")[1].strip(" ").removesuffix("]").strip(" "))] = conv_correct_class(parse_var(split[1])) # lol
            else:
                (parse_var(split_call[0]).variables if split_call else variables)[split[0].strip(" ")]["val"] = conv_correct_class(parse_var(split[1]))
        
        if operation == "call":
            info = parse_function_call(line)
            info.pop("on")
            info["from"] = line_num
            info["stacktype"] = "call_func"

            ind = 0
            for arg in info["args"]:
                variable = parse_var(arg)
                variables[functions[info["name"]]["args"][ind].strip(" ")] = {
                    "dectype": "vv",
                    "vartype": type(variable),
                    "val": variable,
                    "delete_at": functions[info["name"]]["end_line"] + 1,
                }
                ind += 1
            
            stack.append(info)

            if debug:
                print(f"DEBUG: Called function, printing stack. {stack}")
            
            line_num = functions[info["name"]]["line"]
    
    if called_one_liner:
        called_one_liner = False
        line_num = stack[-1]["from"]
        stack.pop()
            