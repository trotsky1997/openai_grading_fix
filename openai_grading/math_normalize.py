"""
This logic is largely copied from the Hendrycks' MATH release (math_equivalence).
"""
import re
from typing import Optional

def convert_latex_fraction(latex):
    def fix_bracket_extract(numerator):
        left = process_fraction_part(numerator)
        if left.isdigit() or (left.isalpha() and len(left.strip()) == 1):
            left = str(left)
        else:
            left = f'({left})'
        
        return left


    def process_fraction(match):
        numerator = match.group(1)
        denominator = match.group(2)
        
        return f'{fix_bracket_extract(numerator)}/{fix_bracket_extract(denominator)}'

    def process_fraction_part(expression):
        if '\\frac' not in expression:
            return expression
        return re.sub(r'\\frac{([^{}]*(?:{[^{}]*}[^{}]*)*)}{([^{}]*(?:{[^{}]*}[^{}]*)*)}', process_fraction, expression)

    return process_fraction_part(latex)

def latex_to_sympy_style(latex_str):
    # 替换 LaTeX 命令（如 \sin, \cos, \tan）
    expr = re.sub(r'\\(sin|cos|tan|log|exp|sqrt|ln|abs)', lambda m: m.group(1), latex_str)
    
    # # 处理分数 \frac{a}{b} → (a)/(b)
    # expr = re.sub(r'\\frac{([^}]+)}{([^}]+)}', r'(\1)/(\2)', expr)

    expr = re.sub(r'ln\|([^{}]*(?:{[^{}]*}[^{}]*)*)\|', r'ln(\1)', expr)

    expr = re.sub(r'\|([^{}]*(?:{[^{}]*}[^{}]*)*)\|', r'(abs(\1))', expr)
    
    # 在数字和字母/括号之间插入乘号（如 2x → 2*x，3( → 3*(）
    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
    
    # 替换 LaTeX 指数符号（x^2 → x**2）
    expr = expr.replace('^', '**')
    expr = re.sub(r'\*\*\{([^}]+)\}', r'**(\1)', expr)
    
    return expr

def normalize_answer(answer: Optional[str]) -> Optional[str]:
    if answer is None:
        return None
    answer = answer.strip()

    try:
        # Remove enclosing `\text{}`.
        m = re.search("^\\\\text\{(?P<text>.+?)\}$", answer)
        if m is not None:
            answer = m.group("text").strip()
        answer = _strip_string(answer)
        answer = convert_latex_fraction(answer)
        answer = latex_to_sympy_style(answer)
        return answer
    except:
        return answer



def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string


def _remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string


def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0]
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string


def _strip_string(string):
    # linebreaks
    string = string.replace("\n", "")
    # print(string)

    # remove inverse spaces
    string = string.replace("\\!", "")
    # print(string)

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    # print(string)

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    # print(string)

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    # print(string)

    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")

    # remove units (on the right)
    string = _remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) >= 2:
        if len(string.split("=")[0]) <= 4:
            string = string.split("=")[-1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string
