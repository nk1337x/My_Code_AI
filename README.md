# 🧠 Explain-My-Code AI Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**An intelligent code explanation tool powered by AI**

*Understand any code with line-by-line explanations, optimization suggestions, and error detection*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [Examples](#-examples)

</div>

---

## 📋 Overview

**Explain-My-Code AI** is a powerful tool that helps developers understand code by providing:

- 📖 **Line-by-line explanations** in plain English
- ⚡ **Optimization suggestions** to improve code quality
- 🐛 **Potential error detection** before they become bugs
- 📊 **Complexity analysis** for performance insights
- 🎨 **Beautiful UI** with syntax highlighting and color-coded feedback

Whether you're learning to code, reviewing unfamiliar code, or onboarding to a new project, this tool makes understanding code easy and intuitive.

---

## ✨ Features

### 🔍 Code Analysis
- **Multi-language support**: Python, Java, C++ (with Python having the most comprehensive AST-based parsing)
- **Intelligent parsing**: Uses Abstract Syntax Tree (AST) for accurate code understanding
- **Structure extraction**: Automatically identifies functions, classes, loops, conditionals, and more

### 🤖 AI-Powered Explanations
- **Local AI with Ollama**: Run powerful LLMs locally for free
- **Contextual explanations**: Understands code in context, not just line-by-line
- **Plain English**: Complex logic explained in simple, understandable terms

### 🎯 Smart Insights
- **Optimization suggestions**: Color-coded by severity (info, warning, critical)
- **Error detection**: Potential bugs and issues highlighted in red
- **Best practices**: Learn proper coding conventions
- **Complexity analysis**: Time and space complexity insights

### 🖥️ Modern UI
- **Clean, responsive design**: Works on desktop and mobile
- **Syntax highlighting**: Beautiful code display
- **Toggle views**: Switch between line-by-line and summary views
- **Dark theme**: Easy on the eyes

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Quick Start

1. **Clone or download the repository**
```bash
cd Explain-My-Code-AI
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
cd src
streamlit run app.py
```

6. **Open your browser** to `http://localhost:8501`

---

## 📖 Usage

### Basic Usage

1. **Paste your code** in the input area or upload a file
2. **Select the programming language** (or use auto-detect)
3. **Choose your AI provider** in the sidebar
4. **Click "Analyze Code"** to get explanations

### Display Options

Toggle these options in the sidebar to customize your experience:

| Option | Description |
|--------|-------------|
| **Line-by-line explanations** | Show explanation for each line of code |
| **Important lines only** | Focus on complex/important lines |
| **Show optimizations** | Display optimization suggestions |
| **Show potential errors** | Display potential bugs and issues |

### Color Coding

The tool uses intuitive color coding:

| Color | Meaning |
|-------|---------|
| 🟢 Green | Best practices, suggestions, fixes |
| 🟡 Yellow/Orange | Optimization opportunities |
| 🔴 Red | Potential errors or critical issues |
| 🔵 Blue | Informational, complexity analysis |
| ⭐ Yellow Star | Important/complex lines |

---

## ⚙️ Configuration

### AI Providers

#### Ollama (Local, Free) - Recommended
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2

# Run the model
ollama serve
```
No API key required - runs locally on your machine.

#### Mock Provider (Demo Mode)
No configuration needed. Uses pre-built responses for testing the UI without API calls.

---

## 📁 Project Structure

```
Explain-My-Code-AI/
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── src/
│   ├── app.py              # Streamlit web application
│   ├── code_parser.py      # Code parsing module (AST-based)
│   └── ai_explainer.py     # AI explanation generation
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 📚 Examples

### Sample Input

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### Sample Output

#### 📋 Summary
> This Python code implements a recursive Fibonacci number calculator. It defines a function that returns the nth Fibonacci number and then prints the first 10 Fibonacci numbers.

#### 📖 Line-by-Line Explanations

| Line | Code | Explanation |
|------|------|-------------|
| 1 | `def fibonacci(n):` | Defines a function named 'fibonacci' that takes one parameter 'n' |
| 2 | `"""Calculate..."""` | A docstring explaining the function's purpose |
| 3 | `if n <= 1:` | Checks if n is 0 or 1 (base cases) |
| 4 | `return n` | Returns n directly for base cases |
| 5 | `return fibonacci(n-1)...` | Recursively calculates Fibonacci by adding two previous numbers |

#### ⚡ Optimizations

| Severity | Issue | Suggestion |
|----------|-------|------------|
| 🟡 Warning | Recursive approach has O(2^n) complexity | Use memoization or iterative approach for better performance |
| 💡 Info | Consider adding input validation | Check if n is a non-negative integer |

#### ⚠️ Potential Errors

| Severity | Issue | Line | Suggestion |
|----------|-------|------|------------|
| 🟡 Warning | No negative number handling | 3 | Add validation for negative inputs |
| 🟡 Warning | Stack overflow for large n | 5 | Use iterative approach for n > 1000 |

---

## 🔧 Technical Details

### Why AST Parsing?

This tool uses Abstract Syntax Tree (AST) parsing for Python code analysis. Here's why AST is superior:

| Feature | Regex Parsing | AST Parsing |
|---------|---------------|-------------|
| **Accuracy** | Prone to false positives | Precise syntax understanding |
| **Structure** | Flat text matching | Hierarchical tree representation |
| **Context** | No semantic awareness | Understands code semantics |
| **Nesting** | Difficult to handle | Natural tree traversal |
| **Maintenance** | Complex regex patterns | Clean visitor pattern |

### Scaling for Multi-Language Support

The architecture supports easy addition of new languages:

```python
# Current Implementation
- Python: Full AST support via built-in `ast` module
- Java: Regex-based parsing (can upgrade to `javalang`)
- C++: Regex-based parsing (can upgrade to `libclang`)

# Future Enhancements
- Use tree-sitter for universal parsing (40+ languages)
- Add language-specific optimizers
- Implement language-aware best practices
```

---

## 🛠️ Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest

# Run tests
pytest tests/
```

### Code Formatting
```bash
# Install formatters
pip install black flake8

# Format code
black src/

# Check linting
flake8 src/
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - We'd love to hear your ideas
3. **Submit PRs** - Follow the existing code style
4. **Add examples** - More sample code in different languages

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI powered by [Ollama](https://ollama.ai/) for local LLM inference
- Inspired by the need to make code more accessible to everyone

---

<div align="center">

**Made with ❤️ for developers everywhere**

[⬆ Back to Top](#-explain-my-code-ai-tool)

</div>
