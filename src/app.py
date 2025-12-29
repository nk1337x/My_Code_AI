"""
Streamlit Web Application for Explain-My-Code AI Tool

This is the main user interface for the code explanation tool.
Features:
- Clean, modern, responsive UI
- Code input via paste or file upload
- Syntax highlighting for input code
- Line-by-line explanation toggle
- Color-coded optimizations and errors
- Smooth animations
"""

import streamlit as st
import time
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_parser import parse_code, Language
from ai_explainer import get_explainer, CodeExplanation


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Explain My Code AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS STYLES
# ============================================================================

def load_custom_css():
    """Load custom CSS for enhanced UI styling."""
    st.markdown("""
    <style>
    /* ============================================
       DARK THEME - Global Overrides
       ============================================ */
    
    /* Root variables for dark theme */
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #1a1a2e;
        --bg-tertiary: #16213e;
        --bg-card: rgba(255, 255, 255, 0.03);
        --text-primary: #fafafa;
        --text-secondary: #a0aec0;
        --text-muted: #718096;
        --accent-primary: #667eea;
        --accent-secondary: #764ba2;
        --border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Force dark background on everything */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%) !important;
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%) !important;
        color: #fafafa;
    }
    
    /* Sidebar dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* All text elements */
    .stMarkdown, .stText, p, span, label, .stSelectbox label, .stTextInput label {
        color: #e2e8f0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
    
    /* Input fields dark theme */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: #1a1a2e !important;
        color: #fafafa !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="select"] {
        background-color: #1a1a2e !important;
    }
    
    [data-baseweb="menu"] {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: #1a1a2e !important;
        color: #fafafa !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #2d3748 !important;
    }
    
    /* Toggle/Switch styling */
    .stToggle > label > div {
        background-color: #4a5568 !important;
    }
    
    .stToggle > label > div[data-checked="true"] {
        background-color: #667eea !important;
    }
    
    /* File uploader dark theme */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #1a1a2e !important;
        border: 2px dashed rgba(102, 126, 234, 0.4) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: #667eea !important;
        background-color: rgba(102, 126, 234, 0.05) !important;
    }
    
    /* Code blocks */
    .stCodeBlock, [data-testid="stCodeBlock"] {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .stCodeBlock code, pre {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    
    /* Expander dark theme */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #fafafa !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: none !important;
    }
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stNotification"] {
        background-color: #1a1a2e !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* ============================================
       CUSTOM COMPONENT STYLES
       ============================================ */
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #a0a0a0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .stCard {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #1e2837 0%, #151b28 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 1rem 0;
    }
    
    .summary-box h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .summary-box p {
        color: #e2e8f0;
        line-height: 1.6;
    }
    
    /* Line explanation styling */
    .line-explanation {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4a5568;
        transition: all 0.3s ease;
    }
    
    .line-explanation:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(5px);
    }
    
    .line-explanation.important {
        border-left-color: #f6e05e;
        background: rgba(246, 224, 94, 0.05);
    }
    
    .line-number {
        background: #667eea;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 10px;
    }
    
    .line-code {
        font-family: 'Fira Code', 'Monaco', monospace;
        background: rgba(0, 0, 0, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        overflow-x: auto;
        color: #e2e8f0;
    }
    
    .line-explanation-text {
        color: #a0aec0;
        font-size: 0.95rem;
        line-height: 1.5;
        padding-left: 0.5rem;
    }
    
    /* Optimization card - Orange/Yellow */
    .optimization-card {
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.15) 0%, rgba(221, 107, 32, 0.1) 100%);
        border: 1px solid rgba(237, 137, 54, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #ed8936;
    }
    
    .optimization-card.warning {
        background: linear-gradient(135deg, rgba(236, 201, 75, 0.15) 0%, rgba(214, 158, 46, 0.1) 100%);
        border-color: rgba(236, 201, 75, 0.3);
        border-left-color: #ecc94b;
    }
    
    .optimization-card.critical {
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.15) 0%, rgba(229, 62, 62, 0.1) 100%);
        border-color: rgba(245, 101, 101, 0.3);
        border-left-color: #f56565;
    }
    
    .optimization-title {
        color: #ed8936;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .optimization-card.warning .optimization-title {
        color: #ecc94b;
    }
    
    .optimization-card.critical .optimization-title {
        color: #f56565;
    }
    
    /* Error card - Red */
    .error-card {
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.15) 0%, rgba(197, 48, 48, 0.1) 100%);
        border: 1px solid rgba(245, 101, 101, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #f56565;
    }
    
    .error-card.critical {
        background: linear-gradient(135deg, rgba(197, 48, 48, 0.2) 0%, rgba(155, 28, 28, 0.15) 100%);
        border-color: rgba(197, 48, 48, 0.4);
        border-left-color: #c53030;
    }
    
    .error-title {
        color: #fc8181;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-card.critical .error-title {
        color: #feb2b2;
    }
    
    /* Badges */
    .severity-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .severity-info {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
    }
    
    .severity-warning {
        background: rgba(236, 201, 75, 0.2);
        color: #ecc94b;
    }
    
    .severity-error {
        background: rgba(245, 101, 101, 0.2);
        color: #f56565;
    }
    
    .severity-critical {
        background: rgba(197, 48, 48, 0.3);
        color: #feb2b2;
    }
    
    /* Line number badges */
    .line-badge {
        background: rgba(160, 174, 192, 0.2);
        color: #a0aec0;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 4px;
    }
    
    /* Best practices */
    .best-practice {
        background: rgba(72, 187, 120, 0.1);
        border-left: 3px solid #48bb78;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #9ae6b4;
    }
    
    /* Complexity analysis */
    .complexity-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    /* Stats cards */
    .stats-container {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        flex: 1;
        min-width: 120px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 12px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        color: #a0aec0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-bottom: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #fafafa !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1rem !important;
    }
    
    /* Sidebar styling - enhanced */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%) !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(102, 126, 234, 0.4);
        border-radius: 12px;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Suggested code block */
    .suggested-code {
        background: rgba(72, 187, 120, 0.08);
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
    }
    
    .suggested-code-header {
        color: #48bb78;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    /* Scrollbar styling - dark theme */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #7c8ff5 0%, #8a5db8 100%);
    }
    
    /* Button styling - enhanced */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #48bb78 0%, #38a169 100%) !important;
    }
    
    /* Caption text */
    .stCaption {
        color: #718096 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_language_map():
    """Get mapping of display names to language codes."""
    return {
        "Python": "python",
        "Java": "java",
        "C++": "cpp",
        "Auto-detect": None
    }


def render_summary(explanation: CodeExplanation):
    """Render the code summary section."""
    st.markdown(f"""
    <div class="summary-box animate-in">
        <h3>📋 Code Summary</h3>
        <p>{explanation.summary}</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats(explanation: CodeExplanation):
    """Render code statistics."""
    parsed = explanation.parsed_code
    if parsed:
        cols = st.columns(5)
        stats = [
            ("📝", len(parsed.lines), "Lines"),
            ("🔧", len(parsed.functions), "Functions"),
            ("📦", len(parsed.classes), "Classes"),
            ("⚡", len(explanation.optimizations), "Optimizations"),
            ("⚠️", len(explanation.potential_errors), "Issues")
        ]
        
        for col, (icon, value, label) in zip(cols, stats):
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{icon} {value}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)


def render_line_explanations(explanation: CodeExplanation, show_all: bool = True):
    """Render line-by-line explanations."""
    for le in explanation.line_explanations:
        if not show_all and not le.is_important:
            continue
            
        important_class = "important" if le.is_important else ""
        important_badge = "⭐ " if le.is_important else ""
        
        st.markdown(f"""
        <div class="line-explanation {important_class}">
            <span class="line-number">{important_badge}Line {le.line_number}</span>
            <div class="line-code">{le.code}</div>
            <div class="line-explanation-text">{le.explanation}</div>
        </div>
        """, unsafe_allow_html=True)


def render_optimizations(optimizations):
    """Render optimization suggestions with color coding."""
    if not optimizations:
        st.info("✨ No optimization suggestions - your code looks efficient!")
        return
        
    for opt in optimizations:
        severity_class = opt.severity if opt.severity in ['warning', 'critical'] else ''
        severity_icon = {
            'info': '💡',
            'warning': '⚠️',
            'critical': '🔴'
        }.get(opt.severity, '💡')
        
        lines_html = ' '.join([f'<span class="line-badge">L{ln}</span>' for ln in opt.line_numbers])
        
        suggested_code_html = ""
        if opt.suggested_code:
            suggested_code_html = f"""
            <div class="suggested-code">
                <div class="suggested-code-header">💡 Suggested Improvement:</div>
                <code>{opt.suggested_code}</code>
            </div>
            """
        
        st.markdown(f"""
        <div class="optimization-card {severity_class}">
            <div class="optimization-title">
                {severity_icon} {opt.title}
                <span class="severity-badge severity-{opt.severity}">{opt.severity}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">{lines_html}</div>
            <p style="color: #e2e8f0; margin: 0;">{opt.description}</p>
            {suggested_code_html}
        </div>
        """, unsafe_allow_html=True)


def render_errors(errors):
    """Render potential errors with color coding."""
    if not errors:
        st.success("✅ No potential errors detected!")
        return
        
    for err in errors:
        severity_class = "critical" if err.severity == 'critical' else ''
        severity_icon = {
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }.get(err.severity, '⚠️')
        
        lines_html = ' '.join([f'<span class="line-badge">L{ln}</span>' for ln in err.line_numbers])
        
        suggestion_html = ""
        if err.suggestion:
            suggestion_html = f"""
            <div style="margin-top: 0.8rem; padding: 0.8rem; background: rgba(72, 187, 120, 0.1); border-radius: 6px; border-left: 3px solid #48bb78;">
                <strong style="color: #48bb78;">💡 Fix:</strong>
                <span style="color: #9ae6b4;">{err.suggestion}</span>
            </div>
            """
        
        st.markdown(f"""
        <div class="error-card {severity_class}">
            <div class="error-title">
                {severity_icon} {err.title}
                <span class="severity-badge severity-{err.severity}">{err.severity}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">{lines_html}</div>
            <p style="color: #e2e8f0; margin: 0;">{err.description}</p>
            {suggestion_html}
        </div>
        """, unsafe_allow_html=True)


def render_best_practices(practices):
    """Render best practices section."""
    if not practices:
        return
        
    for practice in practices:
        st.markdown(f"""
        <div class="best-practice">
            ✓ {practice}
        </div>
        """, unsafe_allow_html=True)


def render_complexity(complexity):
    """Render complexity analysis."""
    if complexity:
        st.markdown(f"""
        <div class="complexity-box">
            <h4 style="color: #667eea; margin-bottom: 0.5rem;">📊 Complexity Analysis</h4>
            <p style="color: #e2e8f0; margin: 0;">{complexity}</p>
        </div>
        """, unsafe_allow_html=True)


def typing_animation(text: str, speed: float = 0.01):
    """Create a typing animation effect."""
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed)
        time.sleep(speed)
    return placeholder


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Explain My Code AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Understand any code with AI-powered explanations</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # AI Provider Selection
        st.markdown("### 🤖 AI Provider")
        provider = st.selectbox(
            "Select Provider",
            ["Mock (Demo)", "Ollama (Local)"],
            help="Choose the AI provider for code explanations"
        )
        
        # Model input (if needed)
        api_key = None
        model = None
        
        if provider == "Ollama (Local)":
            model = st.text_input("Model Name", value="llama3.2",
                                  help="Enter the Ollama model name")
            st.caption("💡 Make sure Ollama is running: `ollama serve`")
        
        st.markdown("---")
        
        # Language Selection
        st.markdown("### 🌐 Language")
        language = st.selectbox(
            "Programming Language",
            ["Auto-detect", "Python", "Java", "C++"],
            help="Select the programming language or auto-detect"
        )
        
        st.markdown("---")
        
        # Display Options
        st.markdown("### 🎨 Display Options")
        show_line_by_line = st.toggle("Line-by-line explanations", value=True,
                                      help="Show explanation for each line")
        show_important_only = st.toggle("Important lines only", value=False,
                                        help="Only show important/complex lines")
        show_optimizations = st.toggle("Show optimizations", value=True,
                                       help="Display optimization suggestions")
        show_errors = st.toggle("Show potential errors", value=True,
                               help="Display potential errors and issues")
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Explain My Code AI** is an intelligent code analysis tool that:
            
            - 📖 Explains code line-by-line
            - 🎯 Highlights important concepts
            - ⚡ Suggests optimizations
            - 🐛 Detects potential errors
            - 🌐 Supports multiple languages
            
            Built with ❤️ using Streamlit and AI.
            """)
    
    # Initialize session state for code input
    if "code_text" not in st.session_state:
        st.session_state.code_text = ""
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input Code")
        
        # Code input tabs
        input_tab1, input_tab2 = st.tabs(["✍️ Paste Code", "📁 Upload File"])
        
        with input_tab1:
            code_input = st.text_area(
                "Paste your code here:",
                value=st.session_state.code_text,
                height=400,
                placeholder="# Paste your code here...\n\ndef example():\n    pass"
            )
            # Sync to session state
            st.session_state.code_text = code_input
        
        with input_tab2:
            uploaded_file = st.file_uploader(
                "Upload a code file",
                type=["py", "java", "cpp", "c", "js", "ts"],
                help="Upload a code file to analyze"
            )
            
            if uploaded_file:
                code_input = uploaded_file.read().decode("utf-8")
                st.session_state.code_text = code_input
                st.code(code_input, language=get_language_map().get(language, "python"))
        
        # Buttons row
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            analyze_button = st.button("🔍 Analyze Code", type="primary", use_container_width=True)
        with btn_col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.code_text = ""
                st.session_state.pop("explanation", None)
                st.session_state.pop("parsed_code", None)
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Code Preview")
        if code_input:
            lang_code = get_language_map().get(language, "python")
            st.code(code_input, language=lang_code or "python", line_numbers=True)
        else:
            st.info("👈 Paste or upload code to see preview")
    
    # Process and display results
    if analyze_button and code_input:
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        with st.spinner("🔄 Analyzing your code..."):
            # Get provider settings
            provider_map = {
                "Mock (Demo)": "mock",
                "Ollama (Local)": "ollama"
            }
            
            try:
                # Parse the code
                lang_code = get_language_map().get(language)
                parsed_code = parse_code(code_input, language=lang_code)
                
                # Get AI explainer
                explainer = get_explainer(
                    provider=provider_map.get(provider, "mock"),
                    api_key=api_key,
                    model=model
                )
                
                # Generate explanation
                explanation = explainer.explain_code(parsed_code)
                
                # Store in session state for persistence
                st.session_state.explanation = explanation
                st.session_state.parsed_code = parsed_code
                
            except Exception as e:
                st.error(f"❌ Error analyzing code: {str(e)}")
                return
        
        # Display results
        if hasattr(st.session_state, 'explanation'):
            explanation = st.session_state.explanation
            
            # Summary
            render_summary(explanation)
            
            # Stats
            render_stats(explanation)
            
            st.markdown("---")
            
            # Tabbed sections
            tab1, tab2, tab3, tab4 = st.tabs([
                "📖 Explanations", 
                "⚡ Optimizations", 
                "⚠️ Potential Issues",
                "📊 Analysis"
            ])
            
            with tab1:
                if show_line_by_line:
                    st.markdown("### Line-by-Line Explanation")
                    show_all = not show_important_only
                    render_line_explanations(explanation, show_all=show_all)
                else:
                    st.info("Enable 'Line-by-line explanations' in settings to see detailed explanations.")
            
            with tab2:
                if show_optimizations:
                    st.markdown("### 💡 Optimization Suggestions")
                    render_optimizations(explanation.optimizations)
                else:
                    st.info("Enable 'Show optimizations' in settings.")
            
            with tab3:
                if show_errors:
                    st.markdown("### 🔍 Potential Issues")
                    render_errors(explanation.potential_errors)
                else:
                    st.info("Enable 'Show potential errors' in settings.")
            
            with tab4:
                st.markdown("### 📈 Code Analysis")
                
                # Complexity
                render_complexity(explanation.complexity_analysis)
                
                # Best practices
                if explanation.best_practices:
                    st.markdown("#### ✅ Best Practices")
                    render_best_practices(explanation.best_practices)
                
                # Code structure
                if explanation.parsed_code:
                    st.markdown("#### 🏗️ Code Structure")
                    structure = explanation.parsed_code.get_structure_summary()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Language", structure['language'].title())
                    with col2:
                        st.metric("Complexity Score", structure['complexity_score'])
                    with col3:
                        st.metric("Total Elements", 
                                  structure['num_functions'] + structure['num_classes'])
    
    elif not code_input:
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #a0aec0;">
            <h3>👆 Get Started</h3>
            <p>Paste your code in the input area or upload a file, then click "Analyze Code"</p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                Try loading a sample from the sidebar to see how it works!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.85rem; padding: 1rem;">
        Made with ❤️ using Streamlit | Explain-My-Code AI Tool
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
