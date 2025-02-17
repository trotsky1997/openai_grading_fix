from openai_grading.grader import grade_answer as openai_is_equiv
from openai_grading.math_normalize import normalize_answer

def is_equiv(answer1, answer2):
    answer1 = str(answer1)
    answer2 = str(answer2)
    if (
        answer1.strip().replace(" ", "").replace("\n", "").lower()
        == answer2.strip().replace(" ", "").replace("\n", "").lower()
    ):
        return True
    res = openai_is_equiv(normalize_answer(answer1), normalize_answer(answer2))
    print(answer1, answer2, res)
    return res


def lowlevel_extract(string):
    if "\\boxed" not in string:
        return string
    while True:
        if "\\boxed" in string:
            string = string[string.find("\\boxed") + len("\\boxed") :]
        else:
            break
    stack = 0
    count = 0
    for c in string:
        count += 1
        if c == "{":
            stack += 1
        elif c == "}":
            stack -= 1
        if stack == 0:
            break
    string = string[1 : count - 1]
    # print(string)

    return string

def lowlevel_normalize(final_answer):
    for i in range(10):
        final_answer = final_answer.replace(f'C_{{{i}}}','C')

    final_answer = final_answer.replace('\\left','').replace('\\right','').replace('×','*').replace('÷','/').replace('{(x )}','(x)').replace('{(','(').replace(' )}',')').replace('log','ln').replace('\\times','*').replace('\\div','/')
    if final_answer.endswith(' = 24'):
        final_answer = final_answer[:-len(' = 24')]
    if final_answer.endswith(' + C'):
        final_answer = final_answer[:-len(' + C')]
    if final_answer.startswith('f(x) = '):
        final_answer = final_answer[len('f(x) = '):]

    return final_answer

    