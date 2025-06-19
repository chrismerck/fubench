# FUBench - Toy Benchmark from Fractal U Frontier LM Course Summer 2025

## Overview
A pipeline for testing language models' mathematical problem-solving abilities.

## What We've Done
1. Generated 15 diverse mathematical problems (algebra, calculus, linear algebra, etc.)
2. Solved each problem using SymPy (Computer Algebra System) as ground truth
3. Created format-constrained problem prompts with specific answer templates

## Aim
Evaluate LLMs' mathematical reasoning by comparing their solutions against verified CAS results, with structured output formats for automated scoring.

## Key Files
- `PROBLEMS.md` - Original mathematical problems
- `PROBLEMS_PROMPTS.md` - Problems with answer format constraints
- `sympy_*.py` - SymPy solvers for each problem
- `SOLUTION_*.md` - Ground truth solutions from SymPy
