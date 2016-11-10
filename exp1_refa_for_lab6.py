# coding=utf8
import re
import copy

simplify_pattern = re.compile(r'(?P<var_name>[a-zA-Z]+)\s*=\s*(?P<var_value>\d+)')


def is_valid(char):
    if char.isdigit() or char.isalpha() or is_symbol(char):
        return True
    else:
        return False


def is_symbol(char):
    if char in ['+', '*', '-', '*', '^']:
        return True
    else:
        return False


def raise_error(error_message):
    print error_message


class Term(object):
    def __init__(self, num, dic):
        self.Num = num
        self.Dict = dic

    def eva(self, known):
        for key in known:
            if key in self.Dict:
                self.Num *= known[key] ** self.Dict.pop(key)
            else:
                pass

    def diff(self, var):
        __tmp = self.Dict.get(var)
        if __tmp == 0:
            pass
        else:
            self.Num *= __tmp
            self.Dict[var] = __tmp - 1

    def to_string(self):
        st = str(self.Num)
        for k in self.Dict:
            if self.Dict[k] == 0:
                continue
            else:
                st = st + '*' + k + '**' + str(self.Dict[k])
        return st


class Expression(object):
    def __init__(self, result, tup):
        self.Sum = result
        self.Tup = tup

    def eva(self, known):
        res = ''
        for i in self.Tup:
            term = Term(i[0], i[1])
            term.eva(known)
            st = term.to_string()
            try:
                self.Sum += float(st)
            except ValueError:
                res = res + st + '+'
        res += str(self.Sum)
        return res

    def diff(self, var):
        res = ''
        for i in self.Tup:
            term = Term(i[0], i[1])
            if var in term.Dict:
                term.diff(var)
                st = term.to_string()
                res = res + st + '+'
            else:
                pass
        return res[:-1]


class Solution(object):
    def __init__(self, user_input):
        """
        :param user_input:用户输入的原始字符串
        """
        self.user_input = user_input
        self.expression = ""
        self.command = ""
        self.acceptable_expression = ""
        self.data = {}

    def command_or_expression(self):
        """
        :return 1: 化简
        :return 2: 求导
        :return 3: 非法
        :return 4: 结束循环
        """
        if self.user_input == "#####":
            return 4
        elif self.user_input.startswith("!simplify"):
            self.command = self.user_input
            return 1
        elif self.user_input.startswith("!d/d"):
            self.command = self.user_input
            return 2
        else:
            self.expression = self.command
            return 3

    def generate_expression(self):
        """
        :return acceptable_expression: python接受的可运行字符串
        """
        index = 0
        while index < len(self.expression) - 1:
            if self.expression[index].isdigit() and self.expression[index + 1].isalpha():
                self.expression = self.expression[:index + 1] + '*' + self.expression[index + 1:]
            if not (is_valid(self.expression[index]) and is_valid(self.expression[index + 1])):
                raise_error("Invalid Input")
                return False
            index += 1
        acceptable_expression = self.expression
        # 幂运算处理
        if '^' in self.user_input:
            acceptable_expression = self.expression.replace('^', '**')
        # 减号处理
        if '-' in self.user_input:
            acceptable_expression = acceptable_expression.replace('-', '+-')

        self.acceptable_expression = acceptable_expression

        return acceptable_expression

    def generate_var_list(self, acceptable_expression):
        """
        :param acceptable_expression: 可接受的字符串
        :return: 变量列表
        """
        index = 1
        name = ""
        var_list = []
        while index < len(acceptable_expression):
            if acceptable_expression[index - 1].isalpha():
                name += acceptable_expression[index - 1]
                if not acceptable_expression[index].isalpha():
                    if name in var_list:
                        pass
                    else:
                        var_list.append(name)
                    name = ""
            if index == len(acceptable_expression) - 1 and acceptable_expression[index].isalpha():
                name += acceptable_expression[index]
                if name in var_list:
                    pass
                else:
                    var_list.append(name)
                name = ""
            else:
                pass
            index += 1
        return var_list

    def generate_var_data(self, acceptable_expression):
        add_list = acceptable_expression.split('+')
        result = 0
        data_list = []
        for i in add_list:
            try:
                result += eval(i)
            except NameError:
                multiple_list = i.split("*")
                num = 1
                dic = {}
                j = 0
                while j < (len(multiple_list)) - 1:
                    if multiple_list[j].isalpha() and multiple_list[j] not in dic:
                        if multiple_list[j+1] == "":
                            dic[multiple_list[j]] = int(multiple_list[j+2])
                            j += 2
                        else:
                            dic[multiple_list[j]] = 1
                    elif multiple_list[j].isalpha() and multiple_list[j] in dic:
                        if multiple_list[j+1] == "":
                            dic[multiple_list[j]] + int(multiple_list[j+2])
                            j += 2
                        else:
                            dic[multiple_list[j]] += 1
                    else:
                        try:
                            num *= float(multiple_list[j])
                        except ValueError:
                            pass
                    j += 1
                if multiple_list[-1].isalpha():
                    if multiple_list[-1] not in dic:
                        dic[multiple_list[-1]] = 1
                    else:
                        dic[multiple_list[-1]] += 1
                elif multiple_list[-1].isdigit() and j < len(multiple_list):
                    num *= multiple_list[-1]
                data_list.append((int(num), dic))
        return result, tuple(data_list)

    def generate_var_value(self, var_list):
        count = 0
        var_dict = {}
        simplify_match = simplify_pattern.finditer(self.command)
        if simplify_match:
            for match in simplify_match:
                if match.group('var_name') not in var_list:
                    raise_error("No such variable")
                else:
                    try:
                        var_dict[match.group('var_name')] = float(match.group('var_value'))
                    except ValueError:
                        raise_error("Invalid value")
                    count += 1
        if not count:
            raise_error("No variable")
            return False
        else:
            return var_dict

    def diff_var(self, var_list):
        try:
            var = self.user_input.split(" ")[1]
        except IndexError:
            raise_error("Error!")
            return False
        if var in var_list:
            return var
        else:
            raise_error("Error!")
            return False

    def parse(self):

