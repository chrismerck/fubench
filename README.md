# FUBench - Toy Benchmark from Fractal U Frontier LM Course Summer 2025

## Overview
A comprehensive framework for evaluating language models' mathematical problem-solving abilities using dynamically generated problems with verified solutions.

## Features
- **Dynamic Problem Generation**: Multiple problem classes with random parameters
- **Automated Evaluation**: Compare model outputs against ground truth solutions
- **Rich Terminal UI**: Beautiful progress bars and colored output using Rich
- **PDF Reports**: Automatically generate LaTeX reports with formatted equations
- **Flexible Configuration**: Customizable models, prompts, and parameters

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd fubench

# Install dependencies
pip install openai rich

# For PDF generation (optional)
# macOS: brew install --cask mactex
# Ubuntu: sudo apt-get install texlive-full
# Windows: Install MiKTeX from https://miktex.org/
```

## Setup

Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY='your-api-key-here'
```

## Usage

### Basic Example
```bash
python fubench.py
```

### Advanced Example
```bash
python fubench.py --verbose --class SystemOfEquationsProblem --num-problems 10 --pdf --model deepseek/deepseek-r1:free --max-tokens 10000
```

### Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | `deepseek/deepseek-v3-base:free` | OpenRouter model to use |
| `--class` | `IntegerQuadraticProblem` | Problem class to evaluate |
| `--num-problems` | `10` | Number of problems to generate |
| `--max-tokens` | `4000` | Maximum tokens for model response |
| `--output` | `results.json` | Output file for summary results |
| `--verbose` | `False` | Show detailed output during evaluation |
| `--pdf` | `False` | Compile and open PDF report |
| `--prompt-file` | `None` | Custom prompt template file |

## Problem Classes

### Built-in Classes
- `IntegerQuadraticProblem` - Quadratic equations with integer solutions
- `TrigExpressionProblem` - Trigonometric expression simplification
- `DerivativeComputationProblem` - Compute derivatives at specific points
- `SystemOfEquationsProblem` - 3×3 linear systems with unique solutions

### Creating Custom Problem Classes
Implement a class with these methods:
```python
class MyProblem:
    def __init__(self):
        # Initialize problem parameters
        
    def __str__(self):
        # Return problem statement
        
    def prompt(self):
        # Return full prompt for the model
        
    def solve(self):
        # Return the correct answer
        
    def check(self, answer):
        # Validate if answer is correct
```

## Output Files

### Directory Structure
```
fubench/
├── results.json          # Summary results
└── logs/
    ├── fubench_run_*.json    # Detailed logs with all responses
    ├── fubench_report_*.tex  # LaTeX source
    └── fubench_report_*.pdf  # Compiled PDF report
```

### PDF Report Contents
- **Summary**: Model performance statistics
- **Problem Details**: For each problem:
  - Question with rendered LaTeX equations
  - Model's complete response
  - Extracted vs correct answer
  - Visual correctness indicator (✓/✗)

## Example Workflow

1. **Test a specific model on systems of equations**:
   ```bash
   python fubench.py --class SystemOfEquationsProblem --model deepseek/deepseek-r1:free --pdf
   ```

2. **Run comprehensive evaluation with detailed logging**:
   ```bash
   python fubench.py --verbose --num-problems 50 --max-tokens 8000 --pdf
   ```

3. **Use custom prompt template**:
   ```bash
   echo "Solve this step by step: {problem}" > custom_prompt.txt
   python fubench.py --prompt-file custom_prompt.txt
   ```

## Prompt Format

The default prompt expects responses in this format:
```
<think>
[reasoning process]
</think>
<answer>
[final answer]
</answer>
```

Models should provide answers in the exact format requested by each problem class (e.g., JSON arrays for multiple solutions).

## Supported Models

Any model available through OpenRouter, including:
- DeepSeek V3 Base
- DeepSeek R1
- Llama variants
- Mistral models
- And many more...

See [OpenRouter documentation](https://openrouter.ai/docs) for the full list.

## Troubleshooting

### LaTeX/PDF Issues
- Ensure LaTeX is installed (`pdflatex --version`)
- Check `logs/` directory for `.tex` files if PDF generation fails
- Use `--verbose` to see compilation errors

### API Issues
- Verify your API key is set correctly
- Check your OpenRouter credits/limits
- Use `--verbose` to see full error messages

## Contributing

To add new problem types:
1. Add your class to `problems.py`
2. Follow the interface pattern of existing classes
3. Test with `python fubench.py --class YourNewClass`

## Key Files
- `fubench.py` - Main evaluation script
- `problems.py` - Problem class definitions
- `PROBLEMS.md` - Original mathematical problems
- `PROBLEMS_PROMPTS.md` - Problems with answer format constraints
- `sympy_*.py` - SymPy solvers for each problem
- `SOLUTION_*.md` - Ground truth solutions from SymPy