import sys

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
    
    def __str__(self):
        if self.true:
            return "true"
        if self.false:
            return "false"
        if self.maybe:
            return "maybe"
        
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

def parse_var(var: str):
    var = var.strip(" ")

    if variables.get(var):
        return variables.get(var)["val"]
    
    if var.find("====") != -1:
        var = var.split("====")
        return var[0].strip(" ") == var[1].strip(" ") # Funny trick ... same name? same variable.

    if var.find("===") != -1:
        var = var.split("===")
        return parse_var(var[0]) == parse_var(var[1])

    if var.find("==") != -1:
        var = var.split("==")
        l = parse_var(var[0])
        r = parse_var(var[1])
        if l == r:
            return True
        elif type(l) == str:
            return str(r) == l
        elif type(r) == str:
            return r == str(l)
    
    if var.find("=") != -1:
        var = var.split("=")
        l = parse_var(var[0])
        r = parse_var(var[1])
        if l == r:
            return True
        elif type(l) == str:
            return str(r) == l
        elif type(r) == str:
            return r == str(l)
        elif (type(l) == float or type(l) == int or l.lstrip("-").split(".")[0].isnumeric()) and (type(r) == float or type(r) == int or r.lstrip("-").split(".")[0].isnumeric()):
            return round(float(l)) == round(float(r))

    if var.find("+") != -1:
        var = var.split("+")
        out = parse_var(var[0])
        first = False
        for item in var:
            if first:
                out += parse_var(item)
            else:
                first = True
        return out
    
    if var.find("-") != -1:
        var = var.split("-")
        out = parse_var(var[0])
        first = False
        for item in var:
            if first:
                out -= parse_var(item)
            else:
                first = True
        return out
    
    if var.find("*") != -1:
        var = var.split("*")
        out = parse_var(var[0])
        first = False
        for item in var:
            if first:
                out *= parse_var(item)
            else:
                first = True
        return out
    
    if var.find("/") != -1:
        var = var.split("/")
        if parse_var(var[1]) == 0:
            return "undefined"
        return parse_var(var[0]) / parse_var(var[1])

    if var.find("^") != -1:
        var = var.split("^")
        return parse_var(var[0]) ** parse_var(var[1])

    if var.startswith('"') or var.startswith("'"):
        while var.startswith('"') or var.startswith("'"):
            var = var.strip('"')
            var = var.strip("'")
        
        while var.find("{") != -1:
            contained_var = var.split("{")[1].split("}")[0]
            val = parse_var(contained_var)

            currency = var.split("{")[0][-1]
            if not currency in currency_list:
                print(f"ERROR: Line {line_num}, I don't know about that currency.")
                quit()
        
        return var

    if var.lstrip("-").split(".")[0].isnumeric():
        return float(var)
    
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
        return final
    elif var.endswith("]"):
        index = parse_var(var.split("[")[1].removesuffix("]"))
        return variables[var.split("[")[0]]["val"][index]
    
    if var == "true":
        return Bool(True, False, False)
    if var == "false":
        return Bool(False, True, False)
    if var == "maybe":
        return Bool(False, False, True)
    
    # It's probably a string.
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
called_one_liner = False

while line_num < len(text):
    line = text[line_num]
    line_num += 1

    if stepping_through_function:
        num_open_curl_bracket += line.count("{")
        num_open_curl_bracket -= line.count("}")

        if num_open_curl_bracket == 0:
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

    # Remove annoying !s and ?s
    while line.endswith("?") or line.endswith("!") or line.startswith(" ") or line.endswith(" "):
        line = line.removesuffix("?")
        line = line.removesuffix("!")
        line = line.strip(" ")
    
    if line == "":
        continue

    if line.startswith("}"):
        line_num = stack[-1]["from"]
        stack.pop()
        continue

    if line.startswith("print"):
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
    
    if is_function(line.split(" ")[0]):
        info = parse_function_call(line.partition(" ")[2].split("=>")[0])
        info["line"] = line_num
        info["created_within"] = stack[-1] if len(stack) > 0 else "main"
        info.pop("on")
        functions[info["name"]] = info
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
        variable = parse_var(line.split("=")[1])
        split_spaces = line.split(" ")

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
        variables[split_spaces[2]] = new_var

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
            print("Uh oh!")
        
        if operation == "on":
            func_info = parse_function_call(line)
            var_info = variables[func_info["on"]]
            
            if debug:
                print(f"DEBUG: Attempting to call {func_info} on variable {var_info}")

            if var_info["dectype"] == "cc" or var_info["dectype"] == "vc":
                print(f"ERROR: On line {line_num} Can't call functions on this variable!")
                break

            if var_info["vartype"] == str:
                if func_info["name"] == "pop":
                    var_info["val"] = var_info["val"][:-1]
                if func_info["name"] == "push":
                    var_info["val"] += parse_var(func_info["args"][0])
        
        if operation == "assign":
            split = line.split("=")

            if split[0].find("[") != -1:
                variables[split[0].split("[")[0].strip(" ")]["val"][parse_var(split[0].split("[")[1].strip(" ").removesuffix("]").strip(" "))] = conv_correct_class(parse_var(split[1])) # lol
            else:
                variables[split[0].strip(" ")]["val"] = conv_correct_class(parse_var(split[1]))
        
        if operation == "call":
            info = parse_function_call(line)
            info.pop("on")
            info["from"] = line_num

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
            