"""
Code Parser Module for Explain-My-Code AI Tool

This module handles parsing of code in multiple languages (Python, Java, C++)
using Abstract Syntax Tree (AST) for Python and regex-based parsing for others.

WHY AST PARSING?
----------------
AST (Abstract Syntax Tree) parsing provides several advantages:
1. Structural Understanding: AST represents code as a tree structure, making it
   easy to understand the hierarchical relationships between code elements.
2. Accurate Analysis: Unlike regex, AST understands the actual syntax and semantics.
3. Language-Aware: AST knows the difference between a function definition and a string.
4. Reliable Extraction: Extracts functions, classes, loops, conditionals accurately.
5. Maintains Context: Preserves the logical flow and nesting of code structures.

SCALING FOR MULTI-LANGUAGE SUPPORT:
-----------------------------------
- Python: Uses built-in `ast` module (most comprehensive)
- Java: Uses regex patterns (can be enhanced with javalang library)
- C++: Uses regex patterns (can be enhanced with pycparser or libclang)
- Future: Can integrate tree-sitter for universal parsing across 40+ languages
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    UNKNOWN = "unknown"


@dataclass
class CodeElement:
    """Represents a parsed code element."""
    element_type: str  # function, class, loop, conditional, variable, import, comment
    name: str
    line_start: int
    line_end: int
    code_snippet: str
    children: List['CodeElement'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedCode:
    """Contains the complete parsed code structure."""
    language: Language
    raw_code: str
    lines: List[str]
    elements: List[CodeElement]
    imports: List[str]
    functions: List[CodeElement]
    classes: List[CodeElement]
    variables: List[str]
    comments: List[str]
    complexity_score: int = 0
    
    def get_line(self, line_number: int) -> str:
        """Get a specific line of code (1-indexed)."""
        if 1 <= line_number <= len(self.lines):
            return self.lines[line_number - 1]
        return ""
    
    def get_structure_summary(self) -> Dict[str, Any]:
        """Get a summary of the code structure."""
        return {
            "language": self.language.value,
            "total_lines": len(self.lines),
            "num_functions": len(self.functions),
            "num_classes": len(self.classes),
            "num_imports": len(self.imports),
            "num_variables": len(self.variables),
            "complexity_score": self.complexity_score
        }


class PythonASTVisitor(ast.NodeVisitor):
    """
    Custom AST visitor for Python code analysis.
    Extracts detailed information about code structure.
    """
    
    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.elements: List[CodeElement] = []
        self.functions: List[CodeElement] = []
        self.classes: List[CodeElement] = []
        self.imports: List[str] = []
        self.variables: List[str] = []
        self.complexity_score = 0
        
    def _get_code_snippet(self, node: ast.AST) -> str:
        """Extract the code snippet for a node."""
        try:
            start_line = node.lineno - 1
            end_line = getattr(node, 'end_lineno', node.lineno)
            return '\n'.join(self.source_lines[start_line:end_line])
        except (AttributeError, IndexError):
            return ""
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        element = CodeElement(
            element_type="function",
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={
                "args": [arg.arg for arg in node.args.args],
                "decorators": [ast.dump(d) for d in node.decorator_list],
                "docstring": ast.get_docstring(node),
                "is_async": False
            }
        )
        self.elements.append(element)
        self.functions.append(element)
        self.complexity_score += 1
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions."""
        element = CodeElement(
            element_type="async_function",
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={
                "args": [arg.arg for arg in node.args.args],
                "decorators": [ast.dump(d) for d in node.decorator_list],
                "docstring": ast.get_docstring(node),
                "is_async": True
            }
        )
        self.elements.append(element)
        self.functions.append(element)
        self.complexity_score += 2
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        element = CodeElement(
            element_type="class",
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={
                "bases": [ast.dump(b) for b in node.bases],
                "decorators": [ast.dump(d) for d in node.decorator_list],
                "docstring": ast.get_docstring(node),
                "methods": []
            }
        )
        self.elements.append(element)
        self.classes.append(element)
        self.complexity_score += 2
        self.generic_visit(node)
        
    def visit_For(self, node: ast.For):
        """Visit for loops."""
        element = CodeElement(
            element_type="for_loop",
            name="for",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={"has_else": len(node.orelse) > 0}
        )
        self.elements.append(element)
        self.complexity_score += 1
        self.generic_visit(node)
        
    def visit_While(self, node: ast.While):
        """Visit while loops."""
        element = CodeElement(
            element_type="while_loop",
            name="while",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={"has_else": len(node.orelse) > 0}
        )
        self.elements.append(element)
        self.complexity_score += 2
        self.generic_visit(node)
        
    def visit_If(self, node: ast.If):
        """Visit if statements."""
        element = CodeElement(
            element_type="conditional",
            name="if",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={
                "has_else": len(node.orelse) > 0,
                "has_elif": len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
            }
        )
        self.elements.append(element)
        self.complexity_score += 1
        self.generic_visit(node)
        
    def visit_Try(self, node: ast.Try):
        """Visit try-except blocks."""
        element = CodeElement(
            element_type="try_except",
            name="try",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={
                "num_handlers": len(node.handlers),
                "has_finally": len(node.finalbody) > 0,
                "has_else": len(node.orelse) > 0
            }
        )
        self.elements.append(element)
        self.complexity_score += len(node.handlers)
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit from-import statements."""
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign):
        """Visit assignment statements."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.generic_visit(node)
        
    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Visit annotated assignment statements."""
        if isinstance(node.target, ast.Name):
            self.variables.append(node.target.id)
        self.generic_visit(node)
        
    def visit_With(self, node: ast.With):
        """Visit with statements (context managers)."""
        element = CodeElement(
            element_type="context_manager",
            name="with",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            code_snippet=self._get_code_snippet(node),
            metadata={"num_items": len(node.items)}
        )
        self.elements.append(element)
        self.generic_visit(node)


class CodeParser:
    """
    Main code parser class that handles multiple programming languages.
    """
    
    def __init__(self):
        self.supported_languages = [Language.PYTHON, Language.JAVA, Language.CPP]
        
    def detect_language(self, code: str, filename: Optional[str] = None) -> Language:
        """
        Detect the programming language from code content or filename.
        
        Args:
            code: The source code string
            filename: Optional filename with extension
            
        Returns:
            Detected Language enum value
        """
        # Check filename extension first
        if filename:
            ext = filename.lower().split('.')[-1]
            extension_map = {
                'py': Language.PYTHON,
                'java': Language.JAVA,
                'cpp': Language.CPP,
                'cc': Language.CPP,
                'cxx': Language.CPP,
                'c': Language.CPP,
                'h': Language.CPP,
                'hpp': Language.CPP
            }
            if ext in extension_map:
                return extension_map[ext]
        
        # Detect from code patterns
        python_patterns = [
            r'^\s*def\s+\w+\s*\(',
            r'^\s*class\s+\w+.*:',
            r'^\s*import\s+\w+',
            r'^\s*from\s+\w+\s+import',
            r'print\s*\(',
            r':\s*$'
        ]
        
        java_patterns = [
            r'public\s+class\s+\w+',
            r'public\s+static\s+void\s+main',
            r'private\s+\w+\s+\w+;',
            r'System\.out\.println',
            r'import\s+java\.',
            r'@Override'
        ]
        
        cpp_patterns = [
            r'#include\s*<',
            r'#include\s*"',
            r'using\s+namespace\s+std',
            r'int\s+main\s*\(',
            r'std::',
            r'cout\s*<<',
            r'cin\s*>>'
        ]
        
        scores = {
            Language.PYTHON: sum(1 for p in python_patterns if re.search(p, code, re.MULTILINE)),
            Language.JAVA: sum(1 for p in java_patterns if re.search(p, code, re.MULTILINE)),
            Language.CPP: sum(1 for p in cpp_patterns if re.search(p, code, re.MULTILINE))
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return Language.UNKNOWN
    
    def parse(self, code: str, language: Optional[Language] = None, 
              filename: Optional[str] = None) -> ParsedCode:
        """
        Parse code and extract structural information.
        
        Args:
            code: The source code to parse
            language: Optional language specification
            filename: Optional filename for language detection
            
        Returns:
            ParsedCode object with extracted information
        """
        # Detect language if not specified
        if language is None:
            language = self.detect_language(code, filename)
            
        lines = code.split('\n')
        
        # Parse based on language
        if language == Language.PYTHON:
            return self._parse_python(code, lines, language)
        elif language == Language.JAVA:
            return self._parse_java(code, lines, language)
        elif language == Language.CPP:
            return self._parse_cpp(code, lines, language)
        else:
            return self._parse_generic(code, lines, language)
    
    def _parse_python(self, code: str, lines: List[str], language: Language) -> ParsedCode:
        """Parse Python code using AST."""
        try:
            tree = ast.parse(code)
            visitor = PythonASTVisitor(lines)
            visitor.visit(tree)
            
            # Extract comments (AST doesn't capture these)
            comments = self._extract_python_comments(lines)
            
            return ParsedCode(
                language=language,
                raw_code=code,
                lines=lines,
                elements=visitor.elements,
                imports=visitor.imports,
                functions=visitor.functions,
                classes=visitor.classes,
                variables=list(set(visitor.variables)),
                comments=comments,
                complexity_score=visitor.complexity_score
            )
        except SyntaxError as e:
            # If AST parsing fails, fall back to regex parsing
            return self._parse_python_fallback(code, lines, language, str(e))
    
    def _parse_python_fallback(self, code: str, lines: List[str], 
                                language: Language, error: str) -> ParsedCode:
        """Fallback Python parsing using regex when AST fails."""
        elements = []
        functions = []
        classes = []
        imports = []
        variables = []
        comments = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Functions
            func_match = re.match(r'def\s+(\w+)\s*\(', stripped)
            if func_match:
                element = CodeElement(
                    element_type="function",
                    name=func_match.group(1),
                    line_start=i,
                    line_end=i,
                    code_snippet=line
                )
                elements.append(element)
                functions.append(element)
                
            # Classes
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                element = CodeElement(
                    element_type="class",
                    name=class_match.group(1),
                    line_start=i,
                    line_end=i,
                    code_snippet=line
                )
                elements.append(element)
                classes.append(element)
                
            # Imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
                
            # Comments
            if '#' in line:
                comment_start = line.index('#')
                comments.append(line[comment_start:])
                
        return ParsedCode(
            language=language,
            raw_code=code,
            lines=lines,
            elements=elements,
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            comments=comments,
            complexity_score=len(elements)
        )
    
    def _extract_python_comments(self, lines: List[str]) -> List[str]:
        """Extract comments from Python code."""
        comments = []
        in_multiline = False
        multiline_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # Single line comments
            if '#' in line and not in_multiline:
                comment_start = line.index('#')
                # Make sure it's not inside a string
                before_hash = line[:comment_start]
                if before_hash.count('"') % 2 == 0 and before_hash.count("'") % 2 == 0:
                    comments.append(line[comment_start:].strip())
                    
            # Docstrings (triple quotes)
            if '"""' in stripped or "'''" in stripped:
                quote_type = '"""' if '"""' in stripped else "'''"
                count = stripped.count(quote_type)
                if count == 1:
                    in_multiline = not in_multiline
                    multiline_char = quote_type if in_multiline else None
                elif count >= 2 and not in_multiline:
                    # Single line docstring
                    comments.append(stripped)
                    
        return comments
    
    def _parse_java(self, code: str, lines: List[str], language: Language) -> ParsedCode:
        """Parse Java code using regex patterns."""
        elements = []
        functions = []
        classes = []
        imports = []
        variables = []
        comments = []
        complexity_score = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Class definitions
            class_match = re.search(r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)', stripped)
            if class_match:
                element = CodeElement(
                    element_type="class",
                    name=class_match.group(1),
                    line_start=i,
                    line_end=i,
                    code_snippet=line
                )
                elements.append(element)
                classes.append(element)
                complexity_score += 2
                
            # Method definitions
            method_match = re.search(
                r'(?:public|private|protected)?\s*(?:static)?\s*(?:\w+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*\{?',
                stripped
            )
            if method_match and not class_match and 'class' not in stripped:
                element = CodeElement(
                    element_type="function",
                    name=method_match.group(1),
                    line_start=i,
                    line_end=i,
                    code_snippet=line
                )
                elements.append(element)
                functions.append(element)
                complexity_score += 1
                
            # Imports
            if stripped.startswith('import '):
                imports.append(stripped[7:].rstrip(';'))
                
            # Comments
            if stripped.startswith('//'):
                comments.append(stripped[2:].strip())
            elif '/*' in stripped or stripped.startswith('*'):
                comments.append(stripped)
                
            # Loops and conditionals
            if re.search(r'\bfor\s*\(', stripped):
                elements.append(CodeElement("for_loop", "for", i, i, line))
                complexity_score += 1
            if re.search(r'\bwhile\s*\(', stripped):
                elements.append(CodeElement("while_loop", "while", i, i, line))
                complexity_score += 2
            if re.search(r'\bif\s*\(', stripped):
                elements.append(CodeElement("conditional", "if", i, i, line))
                complexity_score += 1
                
        return ParsedCode(
            language=language,
            raw_code=code,
            lines=lines,
            elements=elements,
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            comments=comments,
            complexity_score=complexity_score
        )
    
    def _parse_cpp(self, code: str, lines: List[str], language: Language) -> ParsedCode:
        """Parse C++ code using regex patterns."""
        elements = []
        functions = []
        classes = []
        imports = []
        variables = []
        comments = []
        complexity_score = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Include statements
            if stripped.startswith('#include'):
                imports.append(stripped)
                
            # Class definitions
            class_match = re.search(r'class\s+(\w+)', stripped)
            if class_match:
                element = CodeElement(
                    element_type="class",
                    name=class_match.group(1),
                    line_start=i,
                    line_end=i,
                    code_snippet=line
                )
                elements.append(element)
                classes.append(element)
                complexity_score += 2
                
            # Function definitions (simplified pattern)
            func_match = re.search(
                r'(?:void|int|float|double|char|bool|string|auto|\w+)\s+(\w+)\s*\([^)]*\)\s*(?:const)?\s*\{?',
                stripped
            )
            if func_match and 'class' not in stripped and not stripped.startswith('#'):
                name = func_match.group(1)
                if name not in ['if', 'while', 'for', 'switch', 'catch']:
                    element = CodeElement(
                        element_type="function",
                        name=name,
                        line_start=i,
                        line_end=i,
                        code_snippet=line
                    )
                    elements.append(element)
                    functions.append(element)
                    complexity_score += 1
                    
            # Comments
            if stripped.startswith('//'):
                comments.append(stripped[2:].strip())
            elif '/*' in stripped or stripped.startswith('*'):
                comments.append(stripped)
                
            # Loops and conditionals
            if re.search(r'\bfor\s*\(', stripped):
                elements.append(CodeElement("for_loop", "for", i, i, line))
                complexity_score += 1
            if re.search(r'\bwhile\s*\(', stripped):
                elements.append(CodeElement("while_loop", "while", i, i, line))
                complexity_score += 2
            if re.search(r'\bif\s*\(', stripped):
                elements.append(CodeElement("conditional", "if", i, i, line))
                complexity_score += 1
                
        return ParsedCode(
            language=language,
            raw_code=code,
            lines=lines,
            elements=elements,
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            comments=comments,
            complexity_score=complexity_score
        )
    
    def _parse_generic(self, code: str, lines: List[str], language: Language) -> ParsedCode:
        """Generic parsing for unknown languages."""
        return ParsedCode(
            language=language,
            raw_code=code,
            lines=lines,
            elements=[],
            imports=[],
            functions=[],
            classes=[],
            variables=[],
            comments=[],
            complexity_score=0
        )
    
    def get_line_annotations(self, parsed_code: ParsedCode) -> Dict[int, List[str]]:
        """
        Get annotations for each line of code.
        
        Returns a dict mapping line numbers to list of annotations
        (e.g., "function start", "loop", "conditional", etc.)
        """
        annotations = {}
        
        for element in parsed_code.elements:
            line = element.line_start
            if line not in annotations:
                annotations[line] = []
                
            annotation = element.element_type.replace('_', ' ').title()
            if element.name and element.name not in ['for', 'while', 'if', 'try', 'with']:
                annotation += f": {element.name}"
            annotations[line].append(annotation)
            
        return annotations


# Convenience function for quick parsing
def parse_code(code: str, language: Optional[str] = None, 
               filename: Optional[str] = None) -> ParsedCode:
    """
    Quick function to parse code.
    
    Args:
        code: Source code string
        language: Optional language string ('python', 'java', 'cpp')
        filename: Optional filename for language detection
        
    Returns:
        ParsedCode object
    """
    parser = CodeParser()
    
    lang = None
    if language:
        lang_map = {
            'python': Language.PYTHON,
            'java': Language.JAVA,
            'cpp': Language.CPP,
            'c++': Language.CPP,
            'c': Language.CPP
        }
        lang = lang_map.get(language.lower())
        
    return parser.parse(code, lang, filename)


if __name__ == "__main__":
    # Example usage
    sample_python = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        return x + y
        
# Main execution
for i in range(10):
    print(fibonacci(i))
'''
    
    parser = CodeParser()
    result = parser.parse(sample_python)
    
    print("Language:", result.language.value)
    print("Functions:", [f.name for f in result.functions])
    print("Classes:", [c.name for c in result.classes])
    print("Structure:", result.get_structure_summary())
