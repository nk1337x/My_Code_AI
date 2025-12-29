"""
AI Explainer Module for Explain-My-Code AI Tool

This module handles AI-powered code explanation generation using various
AI providers (OpenAI, Anthropic Claude, or local models via Ollama).

The module generates:
1. Line-by-line explanations
2. Overall code summary
3. Optimization suggestions
4. Potential error detection
"""

import os
import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Generator, Any
from enum import Enum
from abc import ABC, abstractmethod

# Import the code parser
from code_parser import ParsedCode, CodeElement, Language


class AIProvider(Enum):
    """Supported AI providers."""
    OLLAMA = "ollama"
    MOCK = "mock"  # For testing without API


@dataclass
class LineExplanation:
    """Explanation for a single line of code."""
    line_number: int
    code: str
    explanation: str
    is_important: bool = False
    
    
@dataclass
class Optimization:
    """Represents a code optimization suggestion."""
    title: str
    description: str
    line_numbers: List[int]
    severity: str = "info"  # info, warning, critical
    suggested_code: Optional[str] = None
    
    
@dataclass
class PotentialError:
    """Represents a potential error or bug."""
    title: str
    description: str
    line_numbers: List[int]
    severity: str = "warning"  # warning, error, critical
    suggestion: Optional[str] = None


@dataclass
class CodeExplanation:
    """Complete explanation of code."""
    summary: str
    line_explanations: List[LineExplanation]
    optimizations: List[Optimization]
    potential_errors: List[PotentialError]
    complexity_analysis: str
    best_practices: List[str]
    parsed_code: Optional[ParsedCode] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary": self.summary,
            "line_explanations": [
                {
                    "line_number": le.line_number,
                    "code": le.code,
                    "explanation": le.explanation,
                    "is_important": le.is_important
                }
                for le in self.line_explanations
            ],
            "optimizations": [
                {
                    "title": opt.title,
                    "description": opt.description,
                    "line_numbers": opt.line_numbers,
                    "severity": opt.severity,
                    "suggested_code": opt.suggested_code
                }
                for opt in self.optimizations
            ],
            "potential_errors": [
                {
                    "title": err.title,
                    "description": err.description,
                    "line_numbers": err.line_numbers,
                    "severity": err.severity,
                    "suggestion": err.suggestion
                }
                for err in self.potential_errors
            ],
            "complexity_analysis": self.complexity_analysis,
            "best_practices": self.best_practices
        }


class PromptTemplates:
    """
    AI prompt templates for code explanation.
    These templates are designed to work with various AI models.
    """
    
    SYSTEM_PROMPT = """You are an expert code explainer and software engineer. 
Your task is to analyze code and provide clear, educational explanations that help 
developers understand what the code does, how it works, and how it could be improved.

When explaining code:
1. Be clear and concise
2. Use simple language that beginners can understand
3. Highlight important concepts
4. Point out potential issues or improvements
5. Be encouraging and educational

Always format your response as valid JSON."""

    CODE_EXPLANATION_PROMPT = """Analyze the following {language} code and provide a comprehensive explanation.

CODE:
```{language}
{code}
```

CODE STRUCTURE INFORMATION:
- Functions: {functions}
- Classes: {classes}
- Imports: {imports}
- Complexity Score: {complexity_score}

Please provide your analysis in the following JSON format:
{{
    "summary": "A 2-3 sentence overall summary of what this code does",
    "line_explanations": [
        {{
            "line_number": 1,
            "code": "the actual code on this line",
            "explanation": "what this line does in simple terms",
            "is_important": true/false
        }}
    ],
    "optimizations": [
        {{
            "title": "Short title of optimization",
            "description": "Detailed explanation of the optimization",
            "line_numbers": [1, 2, 3],
            "severity": "info|warning|critical",
            "suggested_code": "optional improved code snippet"
        }}
    ],
    "potential_errors": [
        {{
            "title": "Short title of the issue",
            "description": "Detailed explanation of the potential error",
            "line_numbers": [1],
            "severity": "warning|error|critical",
            "suggestion": "How to fix this issue"
        }}
    ],
    "complexity_analysis": "Analysis of the code's time and space complexity",
    "best_practices": ["List of best practices this code follows or should follow"]
}}

Important:
- Explain EVERY non-empty line of code
- Mark lines with complex logic or important concepts as is_important: true
- Be specific about line numbers for optimizations and errors
- Focus on educational value in your explanations"""

    LINE_BY_LINE_PROMPT = """Explain the following line of {language} code in simple terms.

Context: This line is part of a larger program. Here's the surrounding code:
```{language}
{context}
```

LINE TO EXPLAIN (Line {line_number}):
```{language}
{line}
```

Provide a clear, simple explanation of what this line does. If it's part of a larger 
construct (like a loop or function), explain its role in that context.

Response should be 1-3 sentences, suitable for someone learning to code."""

    OPTIMIZATION_PROMPT = """Review the following {language} code for potential optimizations:

```{language}
{code}
```

Identify:
1. Performance improvements
2. Code readability improvements
3. Best practice violations
4. Resource efficiency issues

Format each suggestion with:
- Title
- Description
- Affected lines
- Suggested improvement"""

    ERROR_DETECTION_PROMPT = """Analyze the following {language} code for potential bugs, errors, or issues:

```{language}
{code}
```

Look for:
1. Logic errors
2. Edge cases not handled
3. Potential runtime errors
4. Security vulnerabilities
5. Memory leaks or resource issues
6. Type mismatches

For each issue found, provide:
- Title
- Description
- Affected lines
- How to fix it"""


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Generate a streaming response from the AI model."""
        pass


class OllamaProvider(BaseAIProvider):
    """Ollama local model provider."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import requests
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def generate_stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        import requests
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": True
            },
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]


class MockProvider(BaseAIProvider):
    """Mock provider for testing without API calls."""
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return self._generate_mock_response(prompt)
    
    def generate_stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        response = self._generate_mock_response(prompt)
        words = response.split()
        for word in words:
            yield word + " "
            
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response based on the prompt."""
        # This is a simplified mock response for testing
        mock_response = {
            "summary": "This code demonstrates basic programming concepts including functions, loops, and conditionals.",
            "line_explanations": [
                {
                    "line_number": 1,
                    "code": "# Sample code",
                    "explanation": "This is a comment explaining the code.",
                    "is_important": False
                }
            ],
            "optimizations": [
                {
                    "title": "Consider using list comprehension",
                    "description": "List comprehensions are more Pythonic and often faster.",
                    "line_numbers": [1],
                    "severity": "info",
                    "suggested_code": None
                }
            ],
            "potential_errors": [
                {
                    "title": "Missing input validation",
                    "description": "The function doesn't validate its input parameters.",
                    "line_numbers": [1],
                    "severity": "warning",
                    "suggestion": "Add input validation at the beginning of the function."
                }
            ],
            "complexity_analysis": "Time Complexity: O(n), Space Complexity: O(1)",
            "best_practices": [
                "Use meaningful variable names",
                "Add docstrings to functions",
                "Handle edge cases"
            ]
        }
        return json.dumps(mock_response)


class AIExplainer:
    """
    Main AI Explainer class that generates code explanations.
    """
    
    def __init__(self, provider: AIProvider = AIProvider.MOCK, 
                 api_key: Optional[str] = None,
                 model: Optional[str] = None):
        """
        Initialize the AI Explainer.
        
        Args:
            provider: AI provider to use (OPENAI, ANTHROPIC, OLLAMA, MOCK)
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = provider
        self._ai_provider = self._create_provider(provider, api_key, model)
        self.templates = PromptTemplates()
        
    def _create_provider(self, provider: AIProvider, api_key: Optional[str],
                         model: Optional[str]) -> BaseAIProvider:
        """Create the appropriate AI provider instance."""
        if provider == AIProvider.OLLAMA:
            return OllamaProvider(model or "llama3.2")
        else:
            return MockProvider()
    
    def explain_code(self, parsed_code: ParsedCode) -> CodeExplanation:
        """
        Generate a complete explanation of the code.
        
        Args:
            parsed_code: ParsedCode object from the code parser
            
        Returns:
            CodeExplanation object with all explanations
        """
        # Build the prompt
        prompt = self.templates.CODE_EXPLANATION_PROMPT.format(
            language=parsed_code.language.value,
            code=parsed_code.raw_code,
            functions=", ".join([f.name for f in parsed_code.functions]) or "None",
            classes=", ".join([c.name for c in parsed_code.classes]) or "None",
            imports=", ".join(parsed_code.imports[:5]) or "None",  # Limit imports shown
            complexity_score=parsed_code.complexity_score
        )
        
        # Generate the explanation
        try:
            response = self._ai_provider.generate(
                prompt, 
                self.templates.SYSTEM_PROMPT
            )
            return self._parse_explanation_response(response, parsed_code)
        except Exception as e:
            # Return a basic explanation on error
            return self._create_fallback_explanation(parsed_code, str(e))
    
    def explain_code_stream(self, parsed_code: ParsedCode) -> Generator[str, None, None]:
        """
        Generate a streaming explanation of the code.
        
        Args:
            parsed_code: ParsedCode object from the code parser
            
        Yields:
            String chunks of the explanation
        """
        prompt = self.templates.CODE_EXPLANATION_PROMPT.format(
            language=parsed_code.language.value,
            code=parsed_code.raw_code,
            functions=", ".join([f.name for f in parsed_code.functions]) or "None",
            classes=", ".join([c.name for c in parsed_code.classes]) or "None",
            imports=", ".join(parsed_code.imports[:5]) or "None",
            complexity_score=parsed_code.complexity_score
        )
        
        yield from self._ai_provider.generate_stream(
            prompt,
            self.templates.SYSTEM_PROMPT
        )
    
    def explain_line(self, line: str, line_number: int, 
                     context: str, language: str) -> str:
        """
        Explain a single line of code.
        
        Args:
            line: The line of code to explain
            line_number: The line number in the original code
            context: Surrounding code for context
            language: Programming language
            
        Returns:
            Explanation string
        """
        prompt = self.templates.LINE_BY_LINE_PROMPT.format(
            language=language,
            context=context,
            line_number=line_number,
            line=line
        )
        
        return self._ai_provider.generate(prompt, self.templates.SYSTEM_PROMPT)
    
    def _parse_explanation_response(self, response: str, 
                                     parsed_code: ParsedCode) -> CodeExplanation:
        """Parse the AI response into a CodeExplanation object."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Parse line explanations
            line_explanations = []
            for le in data.get("line_explanations", []):
                line_explanations.append(LineExplanation(
                    line_number=le.get("line_number", 0),
                    code=le.get("code", ""),
                    explanation=le.get("explanation", ""),
                    is_important=le.get("is_important", False)
                ))
            
            # Sort line explanations by line number
            line_explanations.sort(key=lambda x: x.line_number)
            
            # Parse optimizations
            optimizations = []
            for opt in data.get("optimizations", []):
                optimizations.append(Optimization(
                    title=opt.get("title", ""),
                    description=opt.get("description", ""),
                    line_numbers=opt.get("line_numbers", []),
                    severity=opt.get("severity", "info"),
                    suggested_code=opt.get("suggested_code")
                ))
            
            # Parse potential errors
            potential_errors = []
            for err in data.get("potential_errors", []):
                potential_errors.append(PotentialError(
                    title=err.get("title", ""),
                    description=err.get("description", ""),
                    line_numbers=err.get("line_numbers", []),
                    severity=err.get("severity", "warning"),
                    suggestion=err.get("suggestion")
                ))
            
            return CodeExplanation(
                summary=data.get("summary", "No summary available."),
                line_explanations=line_explanations,
                optimizations=optimizations,
                potential_errors=potential_errors,
                complexity_analysis=data.get("complexity_analysis", ""),
                best_practices=data.get("best_practices", []),
                parsed_code=parsed_code
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return self._create_fallback_explanation(parsed_code, str(e))
    
    def _create_fallback_explanation(self, parsed_code: ParsedCode, 
                                      error: str = "") -> CodeExplanation:
        """Create a fallback explanation when AI fails."""
        line_explanations = []
        
        for i, line in enumerate(parsed_code.lines, 1):
            stripped = line.strip()
            if stripped:  # Skip empty lines
                explanation = self._generate_basic_explanation(stripped, parsed_code.language)
                line_explanations.append(LineExplanation(
                    line_number=i,
                    code=line,
                    explanation=explanation,
                    is_important=self._is_important_line(stripped)
                ))
        
        return CodeExplanation(
            summary=f"This {parsed_code.language.value} code contains {len(parsed_code.functions)} function(s) and {len(parsed_code.classes)} class(es)." + 
                    (f" (Note: AI explanation failed: {error})" if error else ""),
            line_explanations=line_explanations,
            optimizations=[],
            potential_errors=[],
            complexity_analysis="Unable to analyze complexity without AI.",
            best_practices=[],
            parsed_code=parsed_code
        )
    
    def _generate_basic_explanation(self, line: str, language: Language) -> str:
        """Generate a basic explanation without AI."""
        line_lower = line.lower()
        
        # Common patterns
        if line.startswith('#') or line.startswith('//'):
            return "This is a comment explaining the code."
        elif 'def ' in line:
            match = re.search(r'def\s+(\w+)', line)
            if match:
                return f"Defines a function named '{match.group(1)}'."
        elif 'class ' in line:
            match = re.search(r'class\s+(\w+)', line)
            if match:
                return f"Defines a class named '{match.group(1)}'."
        elif 'import ' in line or 'from ' in line:
            return "Imports a module or library for use in this code."
        elif 'for ' in line:
            return "Starts a loop that iterates over a sequence."
        elif 'while ' in line:
            return "Starts a loop that continues while a condition is true."
        elif 'if ' in line:
            return "Checks a condition and executes code if true."
        elif 'elif ' in line:
            return "Checks another condition if the previous was false."
        elif 'else' in line and ':' in line:
            return "Executes if all previous conditions were false."
        elif 'return ' in line:
            return "Returns a value from the function."
        elif 'print(' in line or 'console.log' in line:
            return "Outputs/displays a value to the console."
        elif '=' in line and '==' not in line:
            return "Assigns a value to a variable."
        elif 'try:' in line:
            return "Starts a block to handle potential errors."
        elif 'except' in line:
            return "Catches and handles specific errors."
        elif 'finally' in line:
            return "Code that always runs, regardless of errors."
        elif 'with ' in line:
            return "Creates a context manager for resource handling."
        elif 'raise ' in line:
            return "Raises an exception/error."
        elif 'assert ' in line:
            return "Checks that a condition is true, raises error if not."
        elif 'lambda ' in line:
            return "Creates an anonymous (inline) function."
        elif line.startswith('"""') or line.startswith("'''"):
            return "Start/end of a docstring (documentation string)."
        else:
            return "Executes an operation or statement."
    
    def _is_important_line(self, line: str) -> bool:
        """Determine if a line is important/complex."""
        important_keywords = [
            'def ', 'class ', 'return ', 'raise ', 'yield ',
            'async ', 'await ', 'try:', 'except', 'finally',
            'with ', 'lambda ', 'assert ', '@'
        ]
        return any(kw in line for kw in important_keywords)


def get_explainer(provider: str = "mock", api_key: Optional[str] = None,
                  model: Optional[str] = None) -> AIExplainer:
    """
    Factory function to create an AI Explainer.
    
    Args:
        provider: Provider name ('ollama', 'mock')
        api_key: API key for the provider (unused, kept for compatibility)
        model: Model name
        
    Returns:
        AIExplainer instance
    """
    provider_map = {
        'ollama': AIProvider.OLLAMA,
        'mock': AIProvider.MOCK
    }
    
    ai_provider = provider_map.get(provider.lower(), AIProvider.MOCK)
    return AIExplainer(ai_provider, api_key, model)


if __name__ == "__main__":
    # Example usage
    from code_parser import parse_code
    
    sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''
    
    # Parse the code
    parsed = parse_code(sample_code, language="python")
    
    # Create explainer (using mock for demo)
    explainer = get_explainer("mock")
    
    # Generate explanation
    explanation = explainer.explain_code(parsed)
    
    print("Summary:", explanation.summary)
    print("\nLine Explanations:")
    for le in explanation.line_explanations:
        print(f"  Line {le.line_number}: {le.explanation}")
