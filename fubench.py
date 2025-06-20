#!/usr/bin/env python3

import os
import json
import argparse
from openai import OpenAI
from problems import *
from random import shuffle
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from datetime import datetime
from pathlib import Path
import subprocess
import platform

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Default prompt template for base model
DEFAULT_PROMPT = """A conversation between User and Assistant. The user asks a question, and the Assistant solves it.
The assistant first thinks about the reasoning process in the mind and then provides the user
with the answer. The reasoning process and answer are enclosed within <think> </think> and
<answer> </answer> tags, respectively, i.e., <think> reasoning process here </think>
<answer> answer here </answer>. User: {problem}. Assistant:"""

def evaluate_problem(problem, model=None, prompt_template=DEFAULT_PROMPT, max_tokens=4000):
    """
    Evaluate a single problem using the specified model via completions API.
    
    Args:
        problem: The problem object
        model: The model identifier for OpenRouter
        prompt_template: The prompt template with {problem} placeholder
        max_tokens: Maximum tokens for the response
    
    Returns:
        dict: Contains the problem, prompt, response, extracted answer, and evaluation
    """
    # Format the prompt with the problem
    prompt = prompt_template.format(problem=problem.prompt())
    
    # Call the model using completions API for base models
    try:
        response = client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.0,  # Deterministic for evaluation
            stop=["</answer>", "\n\nUser:"]  # Stop after answer tag or new user turn
        )
        
        # Extract the response
        full_response = response.choices[0].text
        
        # Try to extract answer between tags
        answer = None
        if "<answer>" in full_response:
            start = full_response.find("<answer>") + len("<answer>")
            # Note: we already stopped at </answer>, but check in case
            end = full_response.find("</answer>", start)
            if end == -1:
                answer = full_response[start:].strip()
            else:
                answer = full_response[start:end].strip()
        
        # Evaluate if the answer is correct
        is_correct = problem.check(answer)
        correct_answer = problem.solve()
        
        return {
            "problem": str(problem),
            "prompt": prompt,
            "full_response": full_response,
            "extracted_answer": answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "model": model
        }
        
    except Exception as e:
        return {
            "problem": str(problem),
            "prompt": prompt,
            "error": str(e),
            "model": model
        }

def generate_latex_report(filename, log_data, args):
    """Generate a LaTeX report with questions, reasoning, answers, and correctness."""
    
    # Escape special LaTeX characters but preserve math mode
    def escape_latex(text, preserve_math=False):
        if text is None:
            return ""
        
        if preserve_math:
            # Split by $ to preserve math mode
            parts = text.split('$')
            result = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Outside math mode
                    result.append(escape_latex(part, preserve_math=False))
                else:  # Inside math mode
                    result.append('$' + part + '$')
            return ''.join(result)
        
        replacements = {
            '\\': r'\textbackslash{}',
            '{': r'\{',
            '}': r'\}',
            '$': r'\$',
            '&': r'\&',
            '%': r'\%',
            '#': r'\#',
            '_': r'\_',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '<': r'\textless{}',
            '>': r'\textgreater{}',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    # Extract reasoning from response
    def extract_reasoning(response):
        if not response:
            return "No reasoning provided"
        
        # Try to extract content between <think> tags
        if "<think>" in response and "</think>" in response:
            start = response.find("<think>") + len("<think>")
            end = response.find("</think>")
            return response[start:end].strip()
        
        # Otherwise return everything before <answer> tag
        if "<answer>" in response:
            return response[:response.find("<answer>")].strip()
        
        return response.strip()
    
    latex_content = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{datetime2}

% Define colors
\definecolor{correctgreen}{RGB}{0,150,0}
\definecolor{incorrectred}{RGB}{200,0,0}
\definecolor{boxgray}{RGB}{240,240,240}

% Setup fancy headers
\pagestyle{fancy}
\fancyhf{}
\lhead{FuBench Evaluation Report}
\rhead{\DTMnow}
\cfoot{\thepage}

% Setup tcolorbox styles
\tcbset{
    base/.style={
        boxrule=0.5pt,
        arc=2mm,
        fonttitle=\bfseries,
        colback=boxgray,
        colframe=black!50
    },
    correct/.style={
        base,
        colframe=correctgreen,
        colbacktitle=correctgreen!20
    },
    incorrect/.style={
        base,
        colframe=incorrectred,
        colbacktitle=incorrectred!20
    }
}

\title{Mathematical Problem Evaluation Report}
\author{Model: """ + escape_latex(args.model) + r"""}
\date{\today}

\begin{document}
\maketitle

\section{Summary}
\begin{itemize}
    \item \textbf{Model:} """ + escape_latex(args.model) + r"""
    \item \textbf{Problem Class:} """ + escape_latex(args.__dict__['class']) + r"""
    \item \textbf{Total Problems:} """ + str(log_data['summary']['total_problems']) + r"""
    \item \textbf{Correct Answers:} """ + str(log_data['summary']['correct_count']) + r"""
    \item \textbf{Accuracy:} """ + f"{log_data['summary']['accuracy']:.1%}" + r"""
\end{itemize}

\section{Detailed Results}

"""
    
    for i, result in enumerate(log_data['detailed_results'], 1):
        # Determine if answer is correct
        is_correct = result.get('is_correct', False)
        box_style = 'correct' if is_correct else 'incorrect'
        
        # Extract components
        problem = result.get('problem', 'No problem text')
        prompt = result.get('prompt', 'No prompt available')
        full_response = result.get('full_response', '')
        reasoning = extract_reasoning(full_response)
        model_answer = result.get('extracted_answer', 'No answer extracted')
        correct_answer = result.get('correct_answer', 'Unknown')
        
        # Add problem to LaTeX
        latex_content += f"""
\\subsection{{Problem {i}}}

\\begin{{tcolorbox}}[colback=gray!5, colframe=gray!50, boxrule=0.5pt, title={{Question}}]
{escape_latex(problem, preserve_math=True)}
\\end{{tcolorbox}}

\\begin{{tcolorbox}}[{box_style}, title={{Model Response}}]
\\textbf{{Full Response:}}
\\begin{{quote}}
{escape_latex(full_response, preserve_math=True)}
\\end{{quote}}

\\textbf{{Extracted Answer:}} {escape_latex(model_answer, preserve_math=True)}

\\textbf{{Correct Answer:}} {escape_latex(correct_answer)}

\\textbf{{Status:}} """
        
        if is_correct:
            latex_content += r"\textcolor{correctgreen}{$\checkmark$ Correct}"
        else:
            latex_content += r"\textcolor{incorrectred}{$\times$ Incorrect}"
            
        latex_content += "\n\\end{tcolorbox}\n\n\\clearpage\n"
    
    latex_content += r"""
\end{document}
"""
    
    # Write to file
    with open(filename, 'w') as f:
        f.write(latex_content)


def main():
    console = Console()
    
    parser = argparse.ArgumentParser(description='Evaluate mathematical problems using OpenRouter')
    parser.add_argument('--model', default='deepseek/deepseek-v3-base:free', help='Model to use')
    parser.add_argument('--class', default='IntegerQuadraticProblem', help='Problem class name to use')
    parser.add_argument('--num-problems', type=int, default=10, help='Number of problems to evaluate')
    parser.add_argument('--output', default='results.json', help='Output file for results')
    parser.add_argument('--prompt-file', help='File containing custom prompt template')
    parser.add_argument('--verbose', action='store_true', help='Show full model responses')
    parser.add_argument('--pdf', action='store_true', help='Compile and open PDF report')
    parser.add_argument('--max-tokens', type=int, default=4000, help='Maximum tokens for model response')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENROUTER_API_KEY environment variable not set")
        console.print("Please set it with: [cyan]export OPENROUTER_API_KEY='your-api-key'[/cyan]")
        return
    
    # Load custom prompt if provided
    prompt_template = DEFAULT_PROMPT
    if args.prompt_file:
        with open(args.prompt_file, 'r') as f:
            prompt_template = f.read()
    
    # Get problem class
    try:
        ProblemClass = eval(args.__dict__['class'])
    except:
        console.print(f"[bold red]Error:[/bold red] Unknown problem class '{args.__dict__['class']}'")
        return
    
    # Get problems
    all_problems = [ProblemClass() for i in range(args.num_problems)]
    shuffle(all_problems)
    problems_to_evaluate = all_problems
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = logs_dir / f"fubench_run_{timestamp}_{args.model.replace('/', '_')}.json"
    
    # Display header
    console.print(Panel.fit(
        f"[bold cyan]Mathematical Problem Evaluation[/bold cyan]\n"
        f"Model: [yellow]{args.model}[/yellow]\n"
        f"Problem Class: [magenta]{args.__dict__['class']}[/magenta]\n"
        f"Problems: [green]{len(problems_to_evaluate)}[/green]\n"
        f"Type: Base model (completions API)",
        title="[bold]FuBench[/bold]",
        border_style="blue"
    ))
    
    results = []
    correct_count = 0
    
    # Create results table
    table = Table(title="Evaluation Results", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Problem", min_width=30)
    table.add_column("Model Answer", min_width=15)
    table.add_column("Correct Answer", min_width=15)
    table.add_column("Status", justify="center", min_width=10)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Evaluating problems...", total=len(problems_to_evaluate))
        
        for i, problem in enumerate(problems_to_evaluate):
            progress.update(task, description=f"[cyan]Problem {i+1}/{len(problems_to_evaluate)}")
            
            # Print problem if verbose
            if args.verbose:
                console.print(f"\n[bold]Problem {i+1}:[/bold] {problem}")
            
            result = evaluate_problem(problem, model=args.model, prompt_template=prompt_template, max_tokens=args.max_tokens)
            
            # Add timestamp and index to result
            result['timestamp'] = datetime.now().isoformat()
            result['problem_index'] = i + 1
            
            if "error" in result:
                if args.verbose:
                    console.print(f"[red]Error: {result['error']}[/red]")
                    
                table.add_row(
                    str(i+1),
                    str(problem),
                    f"[red]Error: {result['error']}[/red]",
                    "-",
                    "[red]✗[/red]"
                )
            else:
                if args.verbose:
                    console.print(f"[dim]Full response:[/dim]")
                    console.print(Panel(result.get('full_response', 'No response'), border_style="dim"))
                    console.print(f"[bold]Extracted answer:[/bold] {result.get('extracted_answer', 'None')}")
                    console.print(f"[bold]Correct answer:[/bold] {result['correct_answer']}")
                    console.print(f"[bold]Status:[/bold] {'[green]Correct[/green]' if result['is_correct'] else '[red]Incorrect[/red]'}")
                
                status_icon = "[green]✓[/green]" if result['is_correct'] else "[red]✗[/red]"
                answer_color = "green" if result['is_correct'] else "red"
                
                table.add_row(
                    str(i+1),
                    str(problem),
                    f"[{answer_color}]{result['extracted_answer'] or 'No answer extracted'}[/{answer_color}]",
                    f"[cyan]{result['correct_answer']}[/cyan]",
                    status_icon
                )
                
                if result['is_correct']:
                    correct_count += 1
            
            results.append(result)
            progress.update(task, advance=1)
    
    # Show results table
    console.print("\n")
    console.print(table)
    
    # Calculate accuracy
    accuracy = correct_count / len(problems_to_evaluate) if len(problems_to_evaluate) > 0 else 0
    
    # Display summary
    summary_color = "green" if accuracy >= 0.8 else "yellow" if accuracy >= 0.5 else "red"
    console.print("\n")
    console.print(Panel(
        f"[bold]Final Results[/bold]\n\n"
        f"Correct: [{summary_color}]{correct_count}[/{summary_color}] / {len(problems_to_evaluate)}\n"
        f"Accuracy: [{summary_color}]{accuracy:.1%}[/{summary_color}]",
        title="[bold]Summary[/bold]",
        border_style=summary_color
    ))
    
    # Save summary results
    output_data = {
        "model": args.model,
        "num_problems": len(problems_to_evaluate),
        "correct_count": correct_count,
        "accuracy": accuracy,
        "results": results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Save detailed log with all prompts and responses
    log_data = {
        "run_info": {
            "timestamp": timestamp,
            "model": args.model,
            "num_problems": len(problems_to_evaluate),
            "prompt_template": prompt_template,
            "max_tokens": args.max_tokens,
            "temperature": 0.0
        },
        "summary": {
            "correct_count": correct_count,
            "total_problems": len(problems_to_evaluate),
            "accuracy": accuracy
        },
        "detailed_results": results
    }
    
    with open(log_filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    # Generate LaTeX report
    tex_filename = logs_dir / f"fubench_report_{timestamp}_{args.model.replace('/', '_')}.tex"
    generate_latex_report(tex_filename, log_data, args)
    
    console.print(f"\n[dim]Summary saved to[/dim] [cyan]{args.output}[/cyan]")
    console.print(f"[dim]Detailed log saved to[/dim] [cyan]{log_filename}[/cyan]")
    console.print(f"[dim]LaTeX report saved to[/dim] [cyan]{tex_filename}[/cyan]")
    
    # Compile and open PDF if requested
    if args.pdf:
        pdf_filename = tex_filename.with_suffix('.pdf')
        
        console.print(f"\n[dim]Compiling LaTeX to PDF...[/dim]")
        
        # Try to compile with pdflatex
        try:
            # Run pdflatex twice to ensure references are resolved
            for i in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(logs_dir), str(tex_filename)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0 and i == 1:  # Only check on second run
                    console.print(f"[yellow]Warning: pdflatex had some issues (this is often okay):[/yellow]")
                    if args.verbose:
                        console.print(f"[dim]{result.stderr[:500]}...[/dim]")
            
            if pdf_filename.exists():
                console.print(f"[green]PDF compiled successfully:[/green] [cyan]{pdf_filename}[/cyan]")
                
                # Open PDF based on platform
                console.print(f"[dim]Opening PDF...[/dim]")
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', str(pdf_filename)])
                elif platform.system() == 'Windows':
                    os.startfile(str(pdf_filename))
                else:  # Linux and others
                    subprocess.run(['xdg-open', str(pdf_filename)])
                    
            else:
                console.print(f"[red]Error: PDF file was not created[/red]")
                
        except FileNotFoundError:
            console.print(f"[red]Error: pdflatex not found. Please install a LaTeX distribution.[/red]")
        except Exception as e:
            console.print(f"[red]Error compiling/opening PDF: {e}[/red]")

if __name__ == "__main__":
    main()