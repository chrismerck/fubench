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

class TrigExpressionProblem:

  def __init__(self):
    self.expression = r"""$\sqrt{ \sec^2 \theta - 1 } \frac{\cos \theta}{\sin \theta}$"""
  
  def __str__(self):
    return self.expression

  def prompt(self):
    return f"Simplify {self.expression}. " +\
            "Give your solution as a single integer."

  def solve(self):
    return "1"
  
  def check(self, answer):
    return answer.strip() == self.solve()


class DerivativeComputationProblem:
    """Compute derivatives of a quadratic at given points and verify answers."""

    def __init__(self):
        # Define the polynomial and the points of evaluation
        self.expression = r"$f(x) = 2 + x - x^2$"
        self._points = [0, 0.5, 1, -10]
        # f'(x) = 1 - 2x, all evaluations are integers
        self._values = {x: int(1 - 2 * x) for x in self._points}

    def __str__(self):
        return self.expression

    def prompt(self):
        pts_labels = ["$f'(0)$", "$f'(\\tfrac12)$", "$f'(1)$", "$f'(-10)$"]
        pts_str = ", ".join(pts_labels)
        return (f"If {self.expression}, compute {pts_str}. "
                "Give your solution as a JSON array of integers.")

    def solve(self):
        """Return the correct answer as JSON array of integers."""
        return json.dumps(list(self._values.values()))

    def check(self, answer):
        """Validate a user's answer."""
        try:
            cleaned = json.loads(answer)
            return json.dumps(cleaned) == self.solve()
        except Exception:
            return False

class SystemOfEquationsProblem:
    """Generate a 3×3 linear system with a unique integer solution and provide solver utilities."""

    @staticmethod
    def _rand():
        """Random integer in [-9, 9]."""
        return randint(-9, 9)

    def __init__(self):
        while True:
            # Hidden integer solution
            self._x = self._rand()
            self._y = self._rand()
            self._z = self._rand()

            # Random coefficients for each equation
            self._a1, self._b1, self._c1 = self._rand(), self._rand(), self._rand()
            self._a2, self._b2, self._c2 = self._rand(), self._rand(), self._rand()
            self._a3, self._b3, self._c3 = self._rand(), self._rand(), self._rand()

            # Compute the constant terms so the chosen solution satisfies each equation
            self._d1 = self._a1 * self._x + self._b1 * self._y + self._c1 * self._z
            self._d2 = self._a2 * self._x + self._b2 * self._y + self._c2 * self._z
            self._d3 = self._a3 * self._x + self._b3 * self._y + self._c3 * self._z

            # Check the determinant of the coefficient matrix to ensure a unique solution
            det = (
                self._a1 * (self._b2 * self._c3 - self._b3 * self._c2)
                - self._b1 * (self._a2 * self._c3 - self._a3 * self._c2)
                + self._c1 * (self._a2 * self._b3 - self._a3 * self._b2)
            )
            if det != 0:
                break  # Unique solution guaranteed

    # Helper to build a pretty inline equation string
    @staticmethod
    def _fmt_eq(a, b, c, d):
        terms = []
        if a:
            terms.append(f"{a}x")
        if b:
            sign = '+' if b > 0 and terms else ''
            terms.append(f"{sign}{b}y")
        if c:
            sign = '+' if c > 0 and terms else ''
            terms.append(f"{sign}{c}z")
        lhs = ' '.join(terms)
        return f"${lhs} = {d}$"

    def __str__(self):
        return self.prompt()

    def prompt(self):
        eq1 = self._fmt_eq(self._a1, self._b1, self._c1, self._d1)
        eq2 = self._fmt_eq(self._a2, self._b2, self._c2, self._d2)
        eq3 = self._fmt_eq(self._a3, self._b3, self._c3, self._d3)
        return (
            "Solve the system of equations: "
            f"{eq1}, {eq2}, {eq3}. "
            "Give your solution as a JSON array of integers [x, y, z]."
        )

    def solve(self):
        """Return the solution in the requested JSON format."""
        return json.dumps([self._x, self._y, self._z])

    def check(self, answer):
        """Validate a user's proposed solution."""
        try:
            guess = json.loads(answer)
            return json.dumps(guess) == self.solve()
        except Exception:
            return False