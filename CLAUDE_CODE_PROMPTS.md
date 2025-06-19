1. I want to test a language model's ability to solve mathematical equations. I propose the following pipeline: we elicit problems from one model, we then solve them using a CAS, rejecting those that are insoluble, and then we test (a probably different model) in it's ability to solve the problem. Please come up with a plan, including which CAS to use, prompt for eliciting problems, and system prompt for the answering model.

---

2. Ok, great. Please come up yourself with a few example problems and save to PROBLEMS.md using --- on a newline as a separator.

---

3. OK great, now please write a new file PROBLEMS.md but put the equations inside $$...$$ and use MathTex format.

---

4. Error producing PDF.  
! Package amsmath Error: Erroneous nesting of equation structures;  
(amsmath)                trying to recover with `aligned'.  

See the amsmath package documentation for explanation.  
Type  H <return>  for immediate help.  
 ...  
l.85 \end{align}

---

5. Now, let's focus on that first problem. How would we feed it into SymPy?

---

6. Keep it simple and just use the latex parser.

---

7. Go ahead and install the deps.

---

8. Great, now please create files sympy_n.py for n=1 to 15 in parallel tasks. For each task, use the latex parser as you did above. Run the program, fixing any bugs, and ultimately outputting the solutions to SOLUTION_n.md.

---

9. OK, let's take a step back and update our PROBLEMS.md to PROBLEMS_PROMPTS.md for each problem to constrain the solution. Please add text to each problem specifying to the answering model what format to use. For example, for the system of equations, ask for the format <solution>x=#,y=#,z=#</solution> where # represent any integer.

