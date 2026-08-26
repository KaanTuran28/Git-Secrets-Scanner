def add(a, b):
    return a + b


def greet(name):
    message = f"Hello, {name}!"
    return message


class Calculator:
    def __init__(self):
        self.history = []

    def compute(self, expression):
        result = eval(expression)
        self.history.append((expression, result))
        return result
