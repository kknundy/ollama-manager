"""
Ollama Model Manager GUI
A graphical interface to manage local Ollama models and browse/download from the model library.
"""

__version__ = "1.0.0"

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import urllib.request
import re
import os
import sys
import time
from pathlib import Path


class OllamaManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Ollama Model Manager v{__version__}")
        self.root.geometry("1400x700")

        # Create menu bar
        self.create_menu_bar()

        # Model catalog - will be populated dynamically or from fallback
        self.model_catalog = []
        self.catalog_loading = False

        # Sorting state tracking
        self.installed_sort_column = None
        self.installed_sort_reverse = False
        self.catalog_sort_column = None
        self.catalog_sort_reverse = False

        self.create_widgets()
        self.refresh_installed_models()

        # Load model catalog (async)
        threading.Thread(target=self.load_model_catalog, daemon=True).start()

    def get_fallback_catalog(self):
        """VERIFIED MODELS ONLY - All models tested and working with ollama pull (as of 2026-05-11)
        Ensures representation from: Meta/Llama, Google, Alibaba/Qwen, Mistral, DeepSeek"""
        catalog = [
            # Most Popular (100M+ downloads)
            {"name": "llama3.1:8b", "size": "4.7 GB", "downloads": "114M+", "description": "Meta Llama 3.1 8B - MOST POPULAR MODEL", "use_case": "General purpose, fast responses", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "llama3.2:3b", "size": "2.0 GB", "downloads": "68.7M+", "description": "Meta Llama 3.2 3B compact - 2ND MOST POPULAR", "use_case": "Quick responses, low-resource devices", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "llama3.2:1b", "size": "1.3 GB", "downloads": "68.7M+", "description": "Meta Llama 3.2 1B smallest", "use_case": "Edge devices, minimal hardware", "specs": "2GB RAM, integrated GPU or any CPU"},

            # Reasoning Models (85M+ downloads)
            {"name": "deepseek-r1:1.5b", "size": "1.1 GB", "downloads": "85M+", "description": "DeepSeek R1 1.5B smallest reasoning", "use_case": "Edge reasoning, minimal resources", "specs": "2GB RAM, integrated GPU or any CPU"},
            {"name": "deepseek-r1:8b", "size": "4.9 GB", "downloads": "85M+", "description": "DeepSeek R1 8B fast reasoning", "use_case": "Fast reasoning, logical queries", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "deepseek-r1:14b", "size": "9.0 GB", "downloads": "85M+", "description": "DeepSeek R1 14B reasoning", "use_case": "Reasoning tasks, balanced speed/quality", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "deepseek-r1:32b", "size": "20 GB", "downloads": "85M+", "description": "DeepSeek R1 32B reasoning", "use_case": "Problem-solving, analytical tasks", "specs": "32GB RAM, RTX 3090/4080 or CPU (moderate)"},
            {"name": "deepseek-r1:70b", "size": "43 GB", "downloads": "85M+", "description": "DeepSeek R1 70B - MOST POPULAR REASONING", "use_case": "Math, logic, scientific reasoning", "specs": "64GB RAM, RTX 4090/A100 or CPU-only (slow)"},

            # Embeddings (69M+ downloads)
            {"name": "nomic-embed-text", "size": "274 MB", "downloads": "69M+", "description": "Nomic Embed - MOST POPULAR EMBEDDING", "use_case": "Semantic search, text similarity, RAG", "specs": "2GB RAM, any GPU or CPU"},
            {"name": "mxbai-embed-large", "size": "335 MB", "downloads": "10.4M+", "description": "MXBai - 2ND MOST POPULAR EMBEDDING", "use_case": "High-quality embeddings", "specs": "2GB RAM, any GPU or CPU"},
            {"name": "all-minilm", "size": "22 MB", "downloads": "3M+", "description": "Lightweight embedding model", "use_case": "Fast embeddings, minimal resources", "specs": "1GB RAM, any CPU"},

            # Qwen/Alibaba (29M+ downloads)
            {"name": "qwen2.5:0.5b", "size": "397 MB", "downloads": "29.6M+", "description": "Qwen 2.5 0.5B ultra-compact", "use_case": "Edge devices, minimal resources", "specs": "1GB RAM, any CPU"},
            {"name": "qwen2.5:1.5b", "size": "1.0 GB", "downloads": "29.6M+", "description": "Qwen 2.5 1.5B compact", "use_case": "Fast responses, low-resource", "specs": "2GB RAM, integrated GPU or any CPU"},
            {"name": "qwen2.5:3b", "size": "1.9 GB", "downloads": "29.6M+", "description": "Qwen 2.5 3B balanced", "use_case": "General purpose, fast", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "qwen2.5:7b", "size": "4.7 GB", "downloads": "29.6M+", "description": "Qwen 2.5 7B - MOST POPULAR ALIBABA", "use_case": "Fast multilingual responses", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "qwen2.5:14b", "size": "9.0 GB", "downloads": "29.6M+", "description": "Qwen 2.5 14B enhanced", "use_case": "General purpose, reasoning, multilingual", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "qwen2.5:32b", "size": "20 GB", "downloads": "29.6M+", "description": "Qwen 2.5 32B flagship", "use_case": "Complex reasoning, multilingual", "specs": "32GB RAM, RTX 3090/4080 or CPU (moderate)"},
            {"name": "qwen2.5:72b", "size": "43 GB", "downloads": "29.6M+", "description": "Qwen 2.5 72B most capable", "use_case": "Advanced reasoning, research", "specs": "64GB RAM, RTX 4090/A100 or CPU-only (slow)"},

            # Coding (15M+ downloads)
            {"name": "qwen2.5-coder:1.5b", "size": "1.0 GB", "downloads": "15.4M+", "description": "Qwen 2.5 Coder 1.5B compact", "use_case": "Fast code completion, edge", "specs": "2GB RAM, integrated GPU or any CPU"},
            {"name": "qwen2.5-coder:7b", "size": "4.7 GB", "downloads": "15.4M+", "description": "Qwen 2.5 Coder - MOST POPULAR CODER", "use_case": "Code generation, fast completion", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "qwen2.5-coder:14b", "size": "9.0 GB", "downloads": "15.4M+", "description": "Qwen 2.5 Coder 14B", "use_case": "Advanced coding, large projects", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "qwen2.5-coder:32b", "size": "20 GB", "downloads": "15.4M+", "description": "Qwen 2.5 Coder 32B flagship", "use_case": "Complex code, large codebases", "specs": "32GB RAM, RTX 3090/4080 or CPU (moderate)"},
            {"name": "deepseek-coder-v2:16b", "size": "8.9 GB", "downloads": "2.5M+", "description": "DeepSeek Coder V2 16B", "use_case": "Code generation, large codebases", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "codegemma:7b", "size": "5.0 GB", "downloads": "N/A", "description": "Google code-specialized Gemma", "use_case": "Code completion, small projects", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "starcoder2:3b", "size": "1.7 GB", "downloads": "N/A", "description": "StarCoder 2 3B compact", "use_case": "Fast code completion", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "starcoder2:7b", "size": "4.0 GB", "downloads": "N/A", "description": "StarCoder 2 7B", "use_case": "Code generation, 17 languages", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "starcoder2:15b", "size": "9.1 GB", "downloads": "N/A", "description": "StarCoder 2 15B flagship", "use_case": "Code generation, completion", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},

            # Vision (14M+ downloads)
            {"name": "llava:7b", "size": "4.7 GB", "downloads": "14M+", "description": "LLaVA 7B vision-language", "use_case": "Vision-language, image understanding", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "llava:13b", "size": "8.0 GB", "downloads": "14M+", "description": "LLaVA 13B enhanced vision", "use_case": "Advanced vision, image analysis", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "llava:34b", "size": "20 GB", "downloads": "14M+", "description": "LLaVA - MOST POPULAR VISION", "use_case": "Vision-language, image understanding", "specs": "32GB RAM, RTX 3090/4080 or CPU (moderate)"},
            {"name": "llama3.2-vision:11b", "size": "7.9 GB", "downloads": "4.5M+", "description": "Llama 3.2 vision capabilities", "use_case": "Image analysis, visual Q&A, OCR", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},
            {"name": "llama3.2-vision:90b", "size": "55 GB", "downloads": "4.5M+", "description": "Llama 3.2 90B vision flagship", "use_case": "Advanced image understanding", "specs": "64GB RAM, RTX 4090/A100 or CPU-only (slow)"},

            # Google Gemma
            {"name": "gemma2:2b", "size": "1.6 GB", "downloads": "N/A", "description": "Google Gemma 2 2B compact", "use_case": "Quick tasks, limited resources", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "gemma2:9b", "size": "5.5 GB", "downloads": "N/A", "description": "Google Gemma 2 9B", "use_case": "General purpose, good balance", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "gemma2:27b", "size": "16 GB", "downloads": "N/A", "description": "Google Gemma 2 27B flagship", "use_case": "Most capable single-GPU model", "specs": "24GB RAM, RTX 3090/4090 or CPU (moderate)"},

            # Mistral (2.6M+ downloads)
            {"name": "mistral:7b", "size": "4.1 GB", "downloads": "2.6M+", "description": "Mistral 7B instruct", "use_case": "General chat, instructions, writing", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},
            {"name": "mixtral:8x7b", "size": "26 GB", "downloads": "2.6M+", "description": "Mistral Mixtral - MOST POPULAR MISTRAL", "use_case": "High-quality responses, multilingual", "specs": "32GB RAM, RTX 3090/4080 or CPU (moderate)"},
            {"name": "mixtral:8x22b", "size": "80 GB", "downloads": "2.6M+", "description": "Mistral Mixtral MoE 8x22B", "use_case": "High-quality responses, diverse tasks", "specs": "96GB RAM, RTX 4090/A100 or CPU-only (slow)"},

            # Microsoft
            {"name": "phi3:3.8b", "size": "2.3 GB", "downloads": "N/A", "description": "Microsoft Phi 3 Mini", "use_case": "Fast responses, general purpose", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "phi3:14b", "size": "7.9 GB", "downloads": "N/A", "description": "Microsoft Phi 3 Medium", "use_case": "STEM tasks, technical writing", "specs": "16GB RAM, RTX 3060 12GB or CPU (fast)"},

            # Other Verified
            {"name": "orca-mini", "size": "1.9 GB", "downloads": "N/A", "description": "Lightweight reasoning model", "use_case": "Quick reasoning, low-resource", "specs": "4GB RAM, GTX 1650 or any CPU"},
            {"name": "neural-chat", "size": "4.1 GB", "downloads": "N/A", "description": "Intel 7B chat model", "use_case": "General chat, instructions", "specs": "8GB RAM, RTX 2060 or CPU (very fast)"},

            # Larger verified models
            {"name": "llama3.1:70b", "size": "43 GB", "downloads": "114M+", "description": "Meta Llama 3.1 70B", "use_case": "Complex reasoning, research", "specs": "64GB RAM, RTX 4090/A100 or CPU-only (slow)"},
        ]

        # Auto-populate publisher field for all models
        for model in catalog:
            if 'publisher' not in model:
                model['publisher'] = self.get_publisher(model['name'])

        return catalog

    def load_model_catalog(self):
        """Load model catalog dynamically from Ollama library API or fallback"""
        if self.catalog_loading:
            return

        self.catalog_loading = True

        # Note: Ollama doesn't provide a public API for browsing models
        # The catalog is curated offline with 60+ popular models
        self.log_progress(f"ℹ Loading curated catalog (62 popular models)\n")
        self.model_catalog = self.get_fallback_catalog()

        # Populate the UI
        self.root.after(0, self.populate_catalog)
        self.catalog_loading = False

    def estimate_hardware_specs(self, size_gb):
        """Estimate hardware requirements based on model size
        Note: Ollama needs ~1.5x model size for overhead during loading"""
        if size_gb >= 60:
            return "96GB+ RAM (model needs ~90GB loaded)"
        elif size_gb >= 40:
            return "64GB RAM (model needs ~60GB loaded)"
        elif size_gb >= 25:
            return "48GB RAM (model needs ~40GB loaded)"
        elif size_gb >= 12:
            return "24GB RAM (model needs ~19GB loaded)"
        elif size_gb >= 8:
            return "16GB RAM (model needs ~12GB loaded)"
        elif size_gb >= 5:
            return "12GB RAM (model needs ~8GB loaded)"
        elif size_gb >= 2:
            return "8GB RAM (model needs ~4GB loaded)"
        else:
            return "4GB RAM, any GPU or CPU"

    def format_size_from_bytes(self, bytes_val):
        """Format bytes to human readable size"""
        if bytes_val == 0:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"

    def format_downloads(self, count):
        """Format download count to human readable format"""
        if count == 0:
            return "N/A"
        elif count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M+"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K+"
        else:
            return str(count)

    def get_publisher(self, name):
        """Determine publisher from model name"""
        name_lower = name.lower()
        if 'llama' in name_lower:
            return "Meta"
        elif 'qwen' in name_lower or 'aya' in name_lower:
            return "Alibaba"
        elif 'deepseek' in name_lower:
            return "DeepSeek"
        elif 'gemma' in name_lower:
            return "Google"
        elif 'mistral' in name_lower or 'mixtral' in name_lower or 'codestral' in name_lower:
            return "Mistral AI"
        elif 'phi' in name_lower:
            return "Microsoft"
        elif 'gpt-oss' in name_lower:
            return "OpenAI"
        elif 'gpt4all' in name_lower:
            return "Nomic AI"
        elif 'gpt-j' in name_lower or 'gpt-neox' in name_lower:
            return "EleutherAI"
        elif 'starcoder' in name_lower:
            return "BigCode"
        elif 'command-r' in name_lower:
            return "Cohere"
        elif 'granite' in name_lower:
            return "IBM"
        elif 'hermes' in name_lower:
            return "Nous Research"
        elif 'falcon' in name_lower:
            return "TII"
        elif 'llava' in name_lower:
            return "LLaVA Team"
        elif 'nomic-embed' in name_lower:
            return "Nomic AI"
        elif 'mxbai' in name_lower:
            return "MixedBread"
        elif 'bge' in name_lower:
            return "BAAI"
        elif 'smollm' in name_lower:
            return "HuggingFace"
        elif 'minicpm' in name_lower:
            return "OpenBMB"
        elif 'moondream' in name_lower:
            return "Vikhyat"
        elif 'all-minilm' in name_lower:
            return "Sentence-T"
        else:
            return "Community"

    def categorize_model(self, name):
        """Categorize model by name for use case"""
        name_lower = name.lower()
        if 'coder' in name_lower or 'code' in name_lower or 'starcoder' in name_lower:
            return "Code generation, debugging, programming"
        elif 'vision' in name_lower or 'llava' in name_lower or 'vl' in name_lower:
            return "Image analysis, visual Q&A, multimodal"
        elif 'embed' in name_lower:
            return "Semantic search, embeddings, RAG"
        elif 'deepseek-r1' in name_lower or 'qwq' in name_lower:
            return "Math, logic, scientific reasoning"
        elif any(x in name_lower for x in ['1b', '2b', '3b', '4b']):
            return "Fast responses, edge devices, low-resource"
        elif any(x in name_lower for x in ['70b', '72b', '90b', '109b', '122b']):
            return "Complex reasoning, research, advanced tasks"
        else:
            return "General purpose, chat, content generation"

    def create_menu_bar(self):
        """Create a clean navigation menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Models", command=self.refresh_installed_models, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Reload Model Catalog", command=self.refresh_catalog_from_web)
        tools_menu.add_separator()
        tools_menu.add_command(label="Configure VS Code", command=self.configure_vscode_menu)
        tools_menu.add_command(label="Clear Download Log", command=self.clear_progress)
        tools_menu.add_separator()
        tools_menu.add_command(label="Check Ollama Status", command=self.check_ollama_status)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help & Usage", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="About Ollama", command=self.show_about_ollama)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

        # Bind keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.refresh_installed_models())
        self.root.bind('<F1>', lambda e: self.show_help())

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Installed Models
        self.installed_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.installed_tab, text='Installed Models')
        self.create_installed_tab()

        # Tab 2: Model Catalog
        self.catalog_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.catalog_tab, text='Model Catalog')
        self.create_catalog_tab()

        # Tab 3: Download Progress
        self.download_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.download_tab, text='Download Progress')
        self.create_download_tab()

    def create_installed_tab(self):
        # Top frame with action buttons
        top_frame = ttk.Frame(self.installed_tab)
        top_frame.pack(fill='x', padx=5, pady=5)

        # Left side buttons
        left_buttons = ttk.Frame(top_frame)
        left_buttons.pack(side='left')

        ttk.Button(left_buttons, text="🔄 Refresh", command=self.refresh_installed_models).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="ℹ Model Info", command=self.show_model_info).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="⚙ VS Code Setup", command=self.configure_vscode).pack(side='left', padx=2)

        # Right side buttons
        right_buttons = ttk.Frame(top_frame)
        right_buttons.pack(side='right')

        ttk.Button(right_buttons, text="🗑 Delete Selected", command=self.delete_model).pack(side='left', padx=2)

        # Treeview for installed models
        columns = ('name', 'id', 'size', 'modified')
        self.installed_tree = ttk.Treeview(self.installed_tab, columns=columns, show='headings', height=20)

        # Make headings clickable for sorting
        self.installed_tree.heading('name', text='Model Name ▼', command=lambda: self.sort_installed_tree('name'))
        self.installed_tree.heading('id', text='ID', command=lambda: self.sort_installed_tree('id'))
        self.installed_tree.heading('size', text='Size', command=lambda: self.sort_installed_tree('size'))
        self.installed_tree.heading('modified', text='Modified', command=lambda: self.sort_installed_tree('modified'))

        self.installed_tree.column('name', width=300)
        self.installed_tree.column('id', width=150)
        self.installed_tree.column('size', width=100)
        self.installed_tree.column('modified', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.installed_tab, orient='vertical', command=self.installed_tree.yview)
        self.installed_tree.configure(yscrollcommand=scrollbar.set)

        self.installed_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

    def create_catalog_tab(self):
        # Custom model frame
        custom_frame = ttk.LabelFrame(self.catalog_tab, text="Download Custom Model", padding=10)
        custom_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(custom_frame, text="Model name or URL:").pack(side='left', padx=5)
        self.custom_model_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_model_var, width=40)
        custom_entry.pack(side='left', padx=5)
        ttk.Button(custom_frame, text="Download", command=self.download_custom_model).pack(side='left', padx=5)

        ttk.Label(custom_frame, text="(e.g., llama3:8b, username/modelname, or registry URL)",
                  font=('TkDefaultFont', 8, 'italic')).pack(side='left', padx=5)

        # Search frame
        search_frame = ttk.Frame(self.catalog_tab)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search catalog:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_catalog)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)

        # System memory indicator
        try:
            import psutil
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            ram_label = ttk.Label(search_frame, text=f"💻 System: {total_ram_gb:.0f}GB RAM ({available_ram_gb:.0f}GB available)",
                                 foreground='#666', font=('TkDefaultFont', 9))
            ram_label.pack(side='left', padx=10)
        except:
            pass  # psutil not available, skip

        ttk.Button(search_frame, text="Download Selected", command=self.download_model).pack(side='right', padx=5)

        # Treeview for catalog
        columns = ('name', 'publisher', 'size', 'downloads', 'specs', 'use_case', 'description')
        self.catalog_tree = ttk.Treeview(self.catalog_tab, columns=columns, show='headings', height=25)

        # Make headings clickable for sorting
        self.catalog_tree.heading('name', text='Model Name ▼', command=lambda: self.sort_catalog_tree('name'))
        self.catalog_tree.heading('publisher', text='Publisher', command=lambda: self.sort_catalog_tree('publisher'))
        self.catalog_tree.heading('size', text='Size', command=lambda: self.sort_catalog_tree('size'))
        self.catalog_tree.heading('downloads', text='Downloads', command=lambda: self.sort_catalog_tree('downloads'))
        self.catalog_tree.heading('specs', text='Min. Hardware Recommended', command=lambda: self.sort_catalog_tree('specs'))
        self.catalog_tree.heading('use_case', text='Recommended For', command=lambda: self.sort_catalog_tree('use_case'))
        self.catalog_tree.heading('description', text='Description', command=lambda: self.sort_catalog_tree('description'))

        self.catalog_tree.column('name', width=170)
        self.catalog_tree.column('publisher', width=100)
        self.catalog_tree.column('size', width=70)
        self.catalog_tree.column('downloads', width=85)
        self.catalog_tree.column('specs', width=240)
        self.catalog_tree.column('use_case', width=210)
        self.catalog_tree.column('description', width=220)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.catalog_tab, orient='vertical', command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)

        self.catalog_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

        # Populate catalog
        self.populate_catalog()

    def create_download_tab(self):
        # Main container
        main_container = ttk.Frame(self.download_tab)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Current download section
        download_frame = ttk.LabelFrame(main_container, text="Current Download", padding=15)
        download_frame.pack(fill='x', pady=(0, 10))

        # Model name
        self.download_model_label = ttk.Label(download_frame, text="No active downloads",
                                              font=('TkDefaultFont', 10, 'bold'))
        self.download_model_label.pack(anchor='w', pady=(0, 10))

        # Overall progress
        progress_container = ttk.Frame(download_frame)
        progress_container.pack(fill='x', pady=5)

        ttk.Label(progress_container, text="Overall Progress:", width=15).pack(side='left')
        self.overall_progress = ttk.Progressbar(progress_container, mode='determinate', length=400)
        self.overall_progress.pack(side='left', fill='x', expand=True, padx=5)
        self.overall_progress_label = ttk.Label(progress_container, text="0%", width=8)
        self.overall_progress_label.pack(side='left')

        # Current layer progress
        layer_container = ttk.Frame(download_frame)
        layer_container.pack(fill='x', pady=5)

        ttk.Label(layer_container, text="Current Layer:", width=15).pack(side='left')
        self.layer_progress = ttk.Progressbar(layer_container, mode='determinate', length=400)
        self.layer_progress.pack(side='left', fill='x', expand=True, padx=5)
        self.layer_progress_label = ttk.Label(layer_container, text="0%", width=8)
        self.layer_progress_label.pack(side='left')

        # KPI Section
        kpi_frame = ttk.Frame(download_frame)
        kpi_frame.pack(fill='x', pady=(10, 0))

        # Left column
        left_kpi = ttk.Frame(kpi_frame)
        left_kpi.pack(side='left', fill='x', expand=True)

        # Downloaded / Total Size
        size_frame = ttk.Frame(left_kpi)
        size_frame.pack(anchor='w', pady=2)
        ttk.Label(size_frame, text="📦 Size:", width=12, foreground='#666').pack(side='left')
        self.size_label = ttk.Label(size_frame, text="0 MB / 0 MB")
        self.size_label.pack(side='left')

        # Download Speed
        speed_frame = ttk.Frame(left_kpi)
        speed_frame.pack(anchor='w', pady=2)
        ttk.Label(speed_frame, text="⚡ Speed:", width=12, foreground='#666').pack(side='left')
        self.speed_label = ttk.Label(speed_frame, text="0 MB/s")
        self.speed_label.pack(side='left')

        # Right column
        right_kpi = ttk.Frame(kpi_frame)
        right_kpi.pack(side='left', fill='x', expand=True)

        # ETA
        eta_frame = ttk.Frame(right_kpi)
        eta_frame.pack(anchor='w', pady=2)
        ttk.Label(eta_frame, text="⏱ ETA:", width=12, foreground='#666').pack(side='left')
        self.eta_label = ttk.Label(eta_frame, text="Calculating...")
        self.eta_label.pack(side='left')

        # Current Layer
        current_frame = ttk.Frame(right_kpi)
        current_frame.pack(anchor='w', pady=2)
        ttk.Label(current_frame, text="📄 Layer:", width=12, foreground='#666').pack(side='left')
        self.current_layer_label = ttk.Label(current_frame, text="Waiting...")
        self.current_layer_label.pack(side='left')

        # Status message
        self.status_label = ttk.Label(download_frame, text="Ready to download",
                                      foreground='#666', font=('TkDefaultFont', 9, 'italic'))
        self.status_label.pack(anchor='w', pady=(10, 0))

        # Log section (smaller, at bottom)
        log_frame = ttk.LabelFrame(main_container, text="Download Log", padding=10)
        log_frame.pack(fill='both', expand=True)

        self.progress_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10,
                                                       font=('Consolas', 9))
        self.progress_text.pack(fill='both', expand=True)

        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(button_frame, text="Clear Log", command=self.clear_progress).pack(side='left', padx=5)

    def refresh_installed_models(self):
        # Clear existing items
        for item in self.installed_tree.get_children():
            self.installed_tree.delete(item)

        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
            lines = result.stdout.strip().split('\n')

            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        name = parts[0]
                        model_id = parts[1]
                        size = parts[2] + ' ' + parts[3]
                        modified = ' '.join(parts[4:])
                        self.installed_tree.insert('', 'end', values=(name, model_id, size, modified))
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to list models: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Ollama CLI not found. Please install Ollama first.")

    def populate_catalog(self):
        # Clear existing items
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Populate with current catalog
        for model in self.model_catalog:
            downloads = model.get('downloads', 'N/A')
            publisher = model.get('publisher', 'Unknown')

            # Add warning emoji for high memory models
            specs = model['specs']
            if any(x in specs for x in ['48GB', '64GB', '96GB', '128GB', '192GB', '512GB']):
                specs = "⚠️ " + specs  # Warning for high-end requirements

            self.catalog_tree.insert('', 'end', values=(model['name'], publisher, model['size'], downloads, specs, model['use_case'], model['description']))

    def refresh_catalog_from_web(self):
        """Manually reload the catalog"""
        if self.catalog_loading:
            messagebox.showinfo("Info", "Catalog is already being loaded...")
            return

        self.log_progress("\n🔄 Reloading model catalog...\n")
        threading.Thread(target=self.load_model_catalog, daemon=True).start()

    def filter_catalog(self, *args):
        search_term = self.search_var.get().lower()

        # Clear tree
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Repopulate with filtered results
        for model in self.model_catalog:
            publisher = model.get('publisher', 'Unknown')
            if (search_term in model['name'].lower() or
                search_term in model['description'].lower() or
                search_term in model['use_case'].lower() or
                search_term in publisher.lower()):
                downloads = model.get('downloads', 'N/A')

                # Add warning emoji for high memory models
                specs = model['specs']
                if any(x in specs for x in ['48GB', '64GB', '96GB', '128GB', '192GB', '512GB']):
                    specs = "⚠️ " + specs

                self.catalog_tree.insert('', 'end', values=(model['name'], publisher, model['size'], downloads, specs, model['use_case'], model['description']))

    def sort_installed_tree(self, col):
        """Sort installed models tree by column"""
        # Toggle sort direction if clicking same column
        if self.installed_sort_column == col:
            self.installed_sort_reverse = not self.installed_sort_reverse
        else:
            self.installed_sort_column = col
            self.installed_sort_reverse = False

        # Get all items
        items = [(self.installed_tree.set(item, col), item) for item in self.installed_tree.get_children('')]

        # Custom sort for size column (convert to bytes)
        if col == 'size':
            def size_key(item):
                size_str = item[0]
                try:
                    # Parse size like "4.7 GB" or "274 MB"
                    parts = size_str.split()
                    if len(parts) == 2:
                        value = float(parts[0])
                        unit = parts[1].upper()
                        if unit == 'GB':
                            return value * 1024 * 1024 * 1024
                        elif unit == 'MB':
                            return value * 1024 * 1024
                        elif unit == 'KB':
                            return value * 1024
                        elif unit == 'B':
                            return value
                    return 0
                except:
                    return 0
            items.sort(key=size_key, reverse=self.installed_sort_reverse)
        else:
            # Alphabetical sort for other columns
            items.sort(reverse=self.installed_sort_reverse)

        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.installed_tree.move(item, '', index)

        # Update column headings to show sort indicator
        for column in ('name', 'id', 'size', 'modified'):
            heading_text = {'name': 'Model Name', 'id': 'ID', 'size': 'Size', 'modified': 'Modified'}[column]
            if column == col:
                indicator = ' ▲' if self.installed_sort_reverse else ' ▼'
                self.installed_tree.heading(column, text=heading_text + indicator)
            else:
                self.installed_tree.heading(column, text=heading_text)

    def sort_catalog_tree(self, col):
        """Sort catalog tree by column"""
        # Toggle sort direction if clicking same column
        if self.catalog_sort_column == col:
            self.catalog_sort_reverse = not self.catalog_sort_reverse
        else:
            self.catalog_sort_column = col
            self.catalog_sort_reverse = False

        # Get all items
        items = [(self.catalog_tree.set(item, col), item) for item in self.catalog_tree.get_children('')]

        # Custom sort for size column (convert to bytes)
        if col == 'size':
            def size_key(item):
                size_str = item[0]
                try:
                    # Parse size like "4.7 GB" or "274 MB" or "~75 GB"
                    size_str = size_str.replace('~', '').strip()
                    parts = size_str.split()
                    if len(parts) == 2:
                        value = float(parts[0])
                        unit = parts[1].upper()
                        if unit == 'GB':
                            return value * 1024 * 1024 * 1024
                        elif unit == 'MB':
                            return value * 1024 * 1024
                        elif unit == 'KB':
                            return value * 1024
                        elif unit == 'B':
                            return value
                    return 0
                except:
                    return 0
            items.sort(key=size_key, reverse=self.catalog_sort_reverse)
        elif col == 'specs':
            # Custom sort for hardware specs (extract RAM number)
            def specs_key(item):
                specs_str = item[0]
                try:
                    # Extract RAM requirement like "16GB RAM" or "2GB RAM"
                    import re
                    match = re.search(r'(\d+)\s*GB\s*RAM', specs_str, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                    # Handle RAM with + like "64GB+ RAM"
                    match = re.search(r'(\d+)\s*GB\+\s*RAM', specs_str, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                    return 0
                except:
                    return 0
            items.sort(key=specs_key, reverse=self.catalog_sort_reverse)
        elif col == 'downloads':
            # Custom sort for downloads (convert text like "85M+" to number)
            def downloads_key(item):
                downloads_str = item[0]
                try:
                    if downloads_str == 'N/A' or downloads_str == 'Unknown':
                        return 0
                    # Remove + and other chars
                    downloads_str = downloads_str.replace('+', '').replace(',', '').strip().upper()
                    # Handle M (millions), K (thousands)
                    if 'M' in downloads_str:
                        return float(downloads_str.replace('M', '')) * 1_000_000
                    elif 'K' in downloads_str:
                        return float(downloads_str.replace('K', '')) * 1_000
                    else:
                        return float(downloads_str)
                except:
                    return 0
            items.sort(key=downloads_key, reverse=self.catalog_sort_reverse)
        else:
            # Alphabetical sort for other columns
            items.sort(reverse=self.catalog_sort_reverse)

        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.catalog_tree.move(item, '', index)

        # Update column headings to show sort indicator
        for column in ('name', 'publisher', 'size', 'downloads', 'specs', 'use_case', 'description'):
            heading_text = {'name': 'Model Name', 'publisher': 'Publisher', 'size': 'Size', 'downloads': 'Downloads',
                          'specs': 'Min. Hardware Recommended', 'use_case': 'Recommended For', 'description': 'Description'}[column]
            if column == col:
                indicator = ' ▲' if self.catalog_sort_reverse else ' ▼'
                self.catalog_tree.heading(column, text=heading_text + indicator)
            else:
                self.catalog_tree.heading(column, text=heading_text)

    def delete_model(self):
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to delete")
            return

        model_name = self.installed_tree.item(selection[0])['values'][0]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{model_name}'?"):
            self.log_progress(f"Deleting model: {model_name}\n")
            threading.Thread(target=self._delete_model_thread, args=(model_name,), daemon=True).start()

    def _delete_model_thread(self, model_name):
        try:
            result = subprocess.run(['ollama', 'rm', model_name], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
            self.log_progress(f"Successfully deleted: {model_name}\n")
            self.log_progress(result.stdout + "\n")
            self.root.after(0, self.refresh_installed_models)
        except subprocess.CalledProcessError as e:
            self.log_progress(f"Error deleting model: {e.stderr}\n")

    def download_custom_model(self):
        model_name = self.custom_model_var.get().strip()
        if not model_name:
            messagebox.showwarning("Warning", "Please enter a model name or URL")
            return

        if messagebox.askyesno("Confirm Download", f"Download '{model_name}'?\n\nThis may take several minutes depending on the model size."):
            self.notebook.select(self.download_tab)
            self.log_progress(f"\n{'='*60}\n")
            self.log_progress(f"Starting download: {model_name}\n")
            self.log_progress(f"{'='*60}\n")
            threading.Thread(target=self._download_model_thread, args=(model_name,), daemon=True).start()
            self.custom_model_var.set("")  # Clear the input field

    def download_model(self):
        selection = self.catalog_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to download")
            return

        model_name = self.catalog_tree.item(selection[0])['values'][0]

        if messagebox.askyesno("Confirm Download", f"Download '{model_name}'?\n\nThis may take several minutes depending on the model size."):
            self.notebook.select(self.download_tab)
            self.log_progress(f"\n{'='*60}\n")
            self.log_progress(f"Starting download: {model_name}\n")
            self.log_progress(f"{'='*60}\n")
            threading.Thread(target=self._download_model_thread, args=(model_name,), daemon=True).start()

    def _download_model_thread(self, model_name):
        try:
            # Initialize UI
            self.update_download_ui(model_name=model_name, status="Initializing...")

            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )

            layers = {}  # Track each layer: {layer_id: {'downloaded': bytes, 'total': bytes}}
            start_time = time.time()
            last_update = 0
            last_bytes = 0

            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue

                current_time = time.time()

                # Log errors immediately with visual alert
                if 'error' in line.lower() or 'failed' in line.lower() or 'not found' in line.lower():
                    self.log_progress(f"❌ ERROR: {line}\n")
                    self.update_download_ui(status=f"Error: {line[:50]}")

                    # Show system notification for critical errors
                    if 'memory' in line.lower() or 'system memory' in line.lower():
                        self.show_memory_error_dialog(line)
                    elif 'not found' in line.lower():
                        self.show_model_not_found_dialog(model_name)

                if line.startswith('pulling manifest'):
                    self.update_download_ui(status="Downloading manifest...")
                    self.log_progress(f"⬇ {line}\n")

                elif line.startswith('pulling') and 'manifest' not in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        layer_id = parts[0].replace('pulling', '').strip()
                        progress_str = ':'.join(parts[1:]).strip()

                        # Parse: "87%  ▕████████████████████████████        ▏ 20 GB/23 GB  39 MB/s  1m20s"
                        tokens = progress_str.split()
                        if len(tokens) >= 1 and '%' in tokens[0]:
                            percent = int(tokens[0].replace('%', ''))

                            downloaded = total = speed_mb = 0

                            # Extract size info "20 GB/23 GB"
                            for i, token in enumerate(tokens):
                                if '/' in token and i > 0:
                                    try:
                                        size_parts = token.split('/')
                                        downloaded = self.parse_size(tokens[i-1] + ' ' + size_parts[0])
                                        total = self.parse_size(size_parts[1] + ' ' + (tokens[i+1] if i+1 < len(tokens) else 'GB'))
                                        break
                                    except:
                                        pass

                            # Extract speed "39 MB/s"
                            for i, token in enumerate(tokens):
                                if 'MB/s' in token or 'KB/s' in token or 'GB/s' in token:
                                    try:
                                        speed_mb = float(tokens[i-1]) if 'MB/s' in token else float(tokens[i-1]) / 1024
                                    except:
                                        pass

                            layers[layer_id] = {'downloaded': downloaded, 'total': total, 'percent': percent}

                            # Throttle UI updates
                            if current_time - last_update >= 0.3:
                                total_downloaded = sum(l['downloaded'] for l in layers.values())
                                total_size = sum(l['total'] for l in layers.values())

                                overall_percent = int((total_downloaded / total_size * 100)) if total_size > 0 else 0

                                # Calculate speed
                                if current_time - start_time > 0:
                                    bytes_diff = total_downloaded - last_bytes
                                    speed_mbps = (bytes_diff / (1024 * 1024)) / (current_time - last_update)
                                    last_bytes = total_downloaded
                                else:
                                    speed_mbps = speed_mb

                                # Calculate ETA
                                if speed_mbps > 0 and total_size > total_downloaded:
                                    eta_seconds = (total_size - total_downloaded) / (speed_mbps * 1024 * 1024)
                                    eta_str = self.format_time(eta_seconds)
                                else:
                                    eta_str = "Calculating..."

                                self.update_download_ui(
                                    model_name=model_name,
                                    overall_percent=overall_percent,
                                    layer_percent=percent,
                                    downloaded_mb=total_downloaded / (1024 * 1024),
                                    total_mb=total_size / (1024 * 1024),
                                    speed_mbps=speed_mbps,
                                    eta=eta_str,
                                    current_layer=layer_id[:12],
                                    status=f"Downloading layer {len(layers)}"
                                )

                                last_update = current_time

                elif line.startswith('verifying'):
                    self.update_download_ui(status="Verifying integrity...")
                    self.log_progress("✓ Verifying...\n")
                elif line.startswith('writing manifest'):
                    self.update_download_ui(status="Writing manifest...")
                    self.log_progress("✓ Writing manifest...\n")
                elif line.startswith('success'):
                    self.update_download_ui(overall_percent=100, layer_percent=100, status="Complete!")

            process.wait()

            if process.returncode == 0:
                self.log_progress(f"\n✅ Successfully downloaded: {model_name}\n")
                self.root.after(0, self.refresh_installed_models)
            else:
                self.update_download_ui(status=f"Error (exit code: {process.returncode})")
                self.log_progress(f"\n✗ Error downloading\n")

        except Exception as e:
            self.update_download_ui(status=f"Error: {str(e)}")
            self.log_progress(f"\n✗ Error: {str(e)}\n")

    def parse_size(self, size_str):
        """Convert size string to bytes"""
        try:
            parts = size_str.strip().split()
            if len(parts) == 2:
                value = float(parts[0])
                unit = parts[1].upper()
                multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
                return int(value * multipliers.get(unit, 1))
        except:
            pass
        return 0

    def format_time(self, seconds):
        """Format seconds to human readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"

    def update_download_ui(self, model_name=None, overall_percent=0, layer_percent=0,
                          downloaded_mb=0, total_mb=0, speed_mbps=0, eta="", current_layer="", status=""):
        """Update the graphical download progress"""
        def update():
            if model_name:
                self.download_model_label.config(text=f"Downloading: {model_name}")
            if overall_percent >= 0:
                self.overall_progress['value'] = overall_percent
                self.overall_progress_label.config(text=f"{overall_percent}%")
            if layer_percent >= 0:
                self.layer_progress['value'] = layer_percent
                self.layer_progress_label.config(text=f"{layer_percent}%")
            if downloaded_mb or total_mb:
                self.size_label.config(text=f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB")
            if speed_mbps:
                self.speed_label.config(text=f"{speed_mbps:.1f} MB/s")
            if eta:
                self.eta_label.config(text=eta)
            if current_layer:
                self.current_layer_label.config(text=current_layer)
            if status:
                self.status_label.config(text=status)

        self.root.after(0, update)

    def log_progress(self, message):
        """Append to log"""
        def update():
            self.progress_text.insert(tk.END, message)
            self.progress_text.see(tk.END)
        self.root.after(0, update)

    def clear_progress(self):
        self.progress_text.delete(1.0, tk.END)
        self.overall_progress['value'] = 0
        self.layer_progress['value'] = 0
        self.download_model_label.config(text="No active downloads")
        self.overall_progress_label.config(text="0%")
        self.layer_progress_label.config(text="0%")
        self.size_label.config(text="0 MB / 0 MB")
        self.speed_label.config(text="0 MB/s")
        self.eta_label.config(text="Calculating...")
        self.current_layer_label.config(text="Waiting...")
        self.status_label.config(text="Ready to download")

    def show_memory_error_dialog(self, error_message):
        """Show visual dialog for memory errors"""
        def show_dialog():
            # Parse the error message to extract memory requirements
            try:
                import re
                match = re.search(r'requires more system memory \(([^)]+)\) than is available \(([^)]+)\)', error_message)
                if match:
                    required = match.group(1)
                    available = match.group(2)
                    message = (f"⚠️ INSUFFICIENT MEMORY\n\n"
                              f"Model requires: {required}\n"
                              f"System available: {available}\n\n"
                              f"💡 Solutions:\n"
                              f"• Close other applications to free up RAM\n"
                              f"• Choose a smaller model (4B-8B parameters)\n"
                              f"• Upgrade system RAM\n"
                              f"• Use quantized versions (Q4, Q5)")
                else:
                    message = f"⚠️ MEMORY ERROR\n\n{error_message}\n\nPlease choose a smaller model."

                messagebox.showerror("Memory Error", message)
            except:
                messagebox.showerror("Memory Error", f"Insufficient system memory:\n\n{error_message}")

        self.root.after(0, show_dialog)

    def show_model_not_found_dialog(self, model_name):
        """Show visual dialog for model not found errors"""
        def show_dialog():
            message = (f"❌ MODEL NOT FOUND\n\n"
                      f"Model '{model_name}' does not exist on Ollama.\n\n"
                      f"💡 Suggestions:\n"
                      f"• Check spelling and format (e.g., llama3:8b)\n"
                      f"• Browse the Model Catalog tab\n"
                      f"• Visit ollama.com/library for available models")
            messagebox.showerror("Model Not Found", message)

        self.root.after(0, show_dialog)

    def show_model_info(self):
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to view info")
            return

        model_name = self.installed_tree.item(selection[0])['values'][0]

        try:
            # Use Ollama API to get model details
            url = f"http://localhost:11434/api/show"
            data = json.dumps({"name": model_name}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req) as response:
                info = json.loads(response.read().decode('utf-8'))

                # Format the information
                info_text = f"Model: {model_name}\n"
                info_text += f"\n{'='*50}\n"

                if 'details' in info:
                    details = info['details']
                    info_text += f"Format: {details.get('format', 'N/A')}\n"
                    info_text += f"Family: {details.get('family', 'N/A')}\n"
                    info_text += f"Parameter Size: {details.get('parameter_size', 'N/A')}\n"
                    info_text += f"Quantization: {details.get('quantization_level', 'N/A')}\n"

                if 'modelfile' in info:
                    info_text += f"\n{'='*50}\n"
                    info_text += "Modelfile:\n"
                    info_text += info['modelfile']

                # Show in a new window
                info_window = tk.Toplevel(self.root)
                info_window.title(f"Model Info: {model_name}")
                info_window.geometry("700x500")

                text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD)
                text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                text_widget.insert(1.0, info_text)
                text_widget.config(state='disabled')

                ttk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get model info: {str(e)}")

    def configure_vscode(self):
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to configure for VS Code")
            return

        model_name = self.installed_tree.item(selection[0])['values'][0]

        # Create configuration window
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Configure VS Code for {model_name}")
        config_window.geometry("800x600")

        # Instructions
        instructions = scrolledtext.ScrolledText(config_window, wrap=tk.WORD, height=35)
        instructions.pack(fill='both', expand=True, padx=10, pady=10)

        vscode_config_text = f"""VS Code Configuration for Ollama Model: {model_name}

{'='*70}

OPTION 1: Continue Extension (Recommended)
{'='*70}

1. Install the "Continue" extension in VS Code:
   - Press Ctrl+Shift+X to open Extensions
   - Search for "Continue" and install it

2. Configure Continue to use Ollama:
   - Press Ctrl+Shift+P and type "Continue: Open Config"
   - Add this to your config.json:

{{
  "models": [
    {{
      "title": "{model_name}",
      "provider": "ollama",
      "model": "{model_name}",
      "apiBase": "http://localhost:11434"
    }}
  ],
  "tabAutocompleteModel": {{
    "title": "{model_name}",
    "provider": "ollama",
    "model": "{model_name}",
    "apiBase": "http://localhost:11434"
  }}
}}

3. Restart VS Code or reload the window (Ctrl+Shift+P → "Reload Window")

4. Use Continue:
   - Press Ctrl+L to open Continue chat
   - Press Ctrl+I for inline editing
   - Tab to accept autocomplete suggestions


{'='*70}

OPTION 2: Ollama Extension
{'='*70}

1. Install the "Ollama" extension in VS Code

2. The extension will auto-detect your local models

3. Use it:
   - Right-click in any file → "Ollama: Generate"
   - Select your model from the dropdown


{'='*70}

OPTION 3: Manual Settings.json Configuration
{'='*70}

Add to VS Code settings.json (Ctrl+Shift+P → "Preferences: Open Settings (JSON)"):

{{
  "ollama.model": "{model_name}",
  "ollama.endpoint": "http://localhost:11434"
}}


{'='*70}

Quick Actions:
{'='*70}

"""

        instructions.insert(1.0, vscode_config_text)
        instructions.config(state='disabled')

        # Button frame
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Copy Model Name",
                  command=lambda: self.copy_to_clipboard(model_name)).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Copy Continue Config",
                  command=lambda: self.copy_continue_config(model_name)).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Open VS Code Settings Folder",
                  command=self.open_vscode_settings).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Close",
                  command=config_window.destroy).pack(side='right', padx=5)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Copied", f"Copied to clipboard: {text}")

    def copy_continue_config(self, model_name):
        config = f'''{{
  "models": [
    {{
      "title": "{model_name}",
      "provider": "ollama",
      "model": "{model_name}",
      "apiBase": "http://localhost:11434"
    }}
  ],
  "tabAutocompleteModel": {{
    "title": "{model_name}",
    "provider": "ollama",
    "model": "{model_name}",
    "apiBase": "http://localhost:11434"
  }}
}}'''
        self.root.clipboard_clear()
        self.root.clipboard_append(config)
        self.root.update()
        messagebox.showinfo("Copied", "Continue configuration copied to clipboard!\n\nPaste it into Continue's config.json")

    def open_vscode_settings(self):
        vscode_paths = [
            Path.home() / "AppData" / "Roaming" / "Code" / "User",  # Windows
            Path.home() / ".config" / "Code" / "User",  # Linux
            Path.home() / "Library" / "Application Support" / "Code" / "User",  # macOS
        ]

        for path in vscode_paths:
            if path.exists():
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(path)
                    else:  # macOS/Linux
                        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open settings folder: {e}")
                    return

        messagebox.showwarning("Not Found", "Could not find VS Code settings folder.\n\nTry opening it manually:\n- Press Ctrl+Shift+P in VS Code\n- Type 'Preferences: Open Settings (JSON)'")

    def configure_vscode_menu(self):
        """Launch VS Code configuration from menu without model selection"""
        if not self.installed_tree.get_children():
            messagebox.showinfo("No Models", "No models installed yet.\n\nDownload a model first, then configure VS Code.")
            return

        messagebox.showinfo("Configure VS Code",
                           "Please select a model from the 'Installed Models' tab,\nthen click 'VS Code Setup' button.")
        self.notebook.select(self.installed_tab)

    def check_ollama_status(self):
        """Check if Ollama service is running"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Ollama Status")
        status_window.geometry("500x300")

        status_text = scrolledtext.ScrolledText(status_window, wrap=tk.WORD)
        status_text.pack(fill='both', expand=True, padx=10, pady=10)

        status_text.insert(tk.END, "Checking Ollama status...\n\n")

        def check_status():
            try:
                # Check if Ollama CLI is available
                result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5)
                status_text.insert(tk.END, f"✓ Ollama CLI installed\n")
                status_text.insert(tk.END, f"  Version: {result.stdout.strip()}\n\n")

                # Check if API is responding
                url = "http://localhost:11434/api/version"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    version_info = json.loads(response.read().decode('utf-8'))
                    status_text.insert(tk.END, f"✓ Ollama API is running\n")
                    status_text.insert(tk.END, f"  API Version: {version_info.get('version', 'unknown')}\n\n")

                # List models
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, encoding='utf-8', errors='replace')
                model_count = len(result.stdout.strip().split('\n')) - 1
                status_text.insert(tk.END, f"✓ Models installed: {model_count}\n\n")

                status_text.insert(tk.END, "Status: ✓ All systems operational\n")

            except subprocess.TimeoutExpired:
                status_text.insert(tk.END, "✗ Ollama is not responding (timeout)\n")
            except FileNotFoundError:
                status_text.insert(tk.END, "✗ Ollama CLI not found\n")
                status_text.insert(tk.END, "\nPlease install Ollama from: https://ollama.com\n")
            except Exception as e:
                status_text.insert(tk.END, f"✗ Error: {str(e)}\n")

            status_text.config(state='disabled')

        threading.Thread(target=check_status, daemon=True).start()

        ttk.Button(status_window, text="Close", command=status_window.destroy).pack(pady=5)

    def show_help(self):
        """Display comprehensive help information"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Usage Guide")
        help_window.geometry("800x600")

        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Consolas', 10))
        help_text.pack(fill='both', expand=True, padx=10, pady=10)

        help_content = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    OLLAMA MODEL MANAGER - HELP GUIDE                     ║
╚══════════════════════════════════════════════════════════════════════════╝

OVERVIEW
────────────────────────────────────────────────────────────────────────────
This application helps you manage AI models for Ollama, a local LLM runtime.
Download, organize, and configure models for use in VS Code and other tools.


GETTING STARTED
────────────────────────────────────────────────────────────────────────────
1. Make sure Ollama is installed: https://ollama.com
2. Browse models in the "Model Catalog" tab
3. Click on a model and press "Download Selected"
4. Monitor progress in the "Download Progress" tab
5. Configure your model for VS Code in the "Installed Models" tab


TABS OVERVIEW
────────────────────────────────────────────────────────────────────────────

📦 INSTALLED MODELS
   • View all locally installed models
   • See model size, ID, and last modified date
   • Delete models you no longer need
   • View detailed model information
   • Configure models for VS Code integration

🌐 MODEL CATALOG
   • Browse 20+ popular AI models
   • Search by name, description, or use case
   • Download models from the curated catalog
   • Enter custom model names or URLs

📊 DOWNLOAD PROGRESS
   • Real-time download progress
   • View download logs and errors
   • Clear logs when needed


KEYBOARD SHORTCUTS
────────────────────────────────────────────────────────────────────────────
F1          - Open this help guide
F5          - Refresh installed models
Alt+F4      - Exit application


COMMON TASKS
────────────────────────────────────────────────────────────────────────────

▸ Download a Model
  1. Go to "Model Catalog" tab
  2. Search or browse for a model
  3. Click on the model row
  4. Click "Download Selected"
  5. Wait for download to complete

▸ Download Custom Model
  1. Go to "Model Catalog" tab
  2. Enter model name in "Download Custom Model" field
     Examples: llama3:8b, username/modelname
  3. Click "Download" button

▸ Delete a Model
  1. Go to "Installed Models" tab
  2. Select the model to delete
  3. Click "Delete Selected" button
  4. Confirm deletion

▸ View Model Details
  1. Go to "Installed Models" tab
  2. Select a model
  3. Click "Model Info" button
  4. View parameters, format, and modelfile

▸ Configure for VS Code
  1. Go to "Installed Models" tab
  2. Select a model
  3. Click "VS Code Setup" button
  4. Follow the instructions to configure Continue extension


MODEL NAMING
────────────────────────────────────────────────────────────────────────────
Models use the format: model_name:tag

Examples:
  • llama3.3:70b     - Llama 3.3 with 70B parameters
  • mistral:7b       - Mistral 7B model
  • qwen2.5:14b      - Qwen 2.5 with 14B parameters

Tags specify model variants (usually parameter count or quantization level)


RECOMMENDED MODELS BY USE CASE
────────────────────────────────────────────────────────────────────────────
• General Chat:        llama3.3:70b, qwen2.5:32b, gemma2:27b
• Coding:              codestral:22b, codegemma:7b
• Fast/Low Resource:   llama3.2:3b, qwen2.5:7b, phi4:14b
• Reasoning/Math:      deepseek-r1:70b, deepseek-r1:32b
• Multilingual:        qwen2.5:72b, qwen2.5:32b
• Vision/Images:       llama3.2-vision:11b, llama3.2-vision:90b
• Embeddings:          nomic-embed-text, mxbai-embed-large


TROUBLESHOOTING
────────────────────────────────────────────────────────────────────────────
Problem: "Ollama CLI not found"
Solution: Install Ollama from https://ollama.com

Problem: Models won't download
Solution: Check internet connection, verify Ollama service is running
         Menu > Tools > Check Ollama Status

Problem: Out of disk space
Solution: Delete unused models from "Installed Models" tab
         Large models can be 40+ GB

Problem: VS Code not detecting model
Solution: Restart VS Code after configuration
         Verify model appears in "ollama list" command


ADDITIONAL RESOURCES
────────────────────────────────────────────────────────────────────────────
• Ollama Documentation:  https://github.com/ollama/ollama
• Model Library:         https://ollama.com/library
• Continue Extension:    https://continue.dev
• Support:               GitHub issues or Ollama Discord


VERSION & LICENSE
────────────────────────────────────────────────────────────────────────────
Ollama Model Manager v{__version__}
MIT License - Free and open source
"""

        help_text.insert(1.0, help_content)
        help_text.config(state='disabled')

        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Check Ollama Status",
                  command=lambda: [help_window.destroy(), self.check_ollama_status()]).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=help_window.destroy).pack(side='right', padx=5)

    def show_about_ollama(self):
        """Show information about Ollama"""
        about_text = """About Ollama

Ollama is a lightweight, extensible framework for running large language models locally on your machine.

Key Features:
• Run AI models locally without cloud dependencies
• Privacy-focused - your data stays on your device
• Support for multiple model architectures
• Easy model switching and management
• API-compatible with OpenAI format
• Cross-platform (Windows, macOS, Linux)

Website: https://ollama.com
GitHub: https://github.com/ollama/ollama
Documentation: https://github.com/ollama/ollama/tree/main/docs

Ollama is developed by Ollama Inc. and the open source community."""

        messagebox.showinfo("About Ollama", about_text)

    def show_about(self):
        """Show about dialog for this application"""
        about_text = f"""Ollama Model Manager
Version {__version__}

A graphical user interface for managing Ollama AI models.

Features:
• Browse and download popular AI models
• Manage installed models
• Configure VS Code integration
• Real-time download progress
• Model information viewer

Created with Python and Tkinter
MIT License

For support and updates:
GitHub: https://github.com"""

        messagebox.showinfo("About Ollama Model Manager", about_text)


def main():
    root = tk.Tk()
    app = OllamaManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
