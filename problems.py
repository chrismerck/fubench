import json
from random import shuffle, randint

def sign(a) -> str:
    return '+' if a > 0 else '-'

class IntegerQuadraticProblem:

  @classmethod
  def all_easy(cls):
    for x1 in range(-99, 100):
      for x2 in range(x1, 100):
        yield cls(x1, x2)

  def __init__(self, x1=None, x2=None):
    if x1 == None:
      x1 = randint(-99, 99)
      x2 = randint(-99, 99)
    self._x1 = x1
    self._x2 = x2
    b = - (self._x1 + self._x2)
    c = self._x1 * self._x2
    self.equation = f"$x^2 {sign(b)} {abs(b)}x {sign(c)} {abs(c)} = 0$"
  
  def __str__(self):
    return self.equation

  def prompt(self):
    return f"Find all solutions of {self.equation}. " +\
            "Give your solution as a JSON array of integers in ascending order."

  def solve(self):
    return json.dumps(sorted({self._x1, self._x2}))
  
  def check(self, answer):
    return json.dumps(sorted(set(json.loads(answer)))) == self.solve()
