"""
Ollama Model Manager GUI
A graphical interface to manage local Ollama models and browse/download from the model library.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import urllib.request
import re
import os
import sys
from pathlib import Path


class OllamaManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Model Manager")
        self.root.geometry("1200x700")

        # Popular models catalog (hardcoded)
        # Note: Ollama doesn't provide a public API to browse models dynamically.
        # This is a curated list of popular models from ollama.com/library
        # Users can download any model using the "Custom Model" input field.
        self.model_catalog = [
            {"name": "llama3.3:70b", "size": "43 GB", "description": "Meta's Llama 3.3 70B model", "use_case": "Complex reasoning, research, advanced chat"},
            {"name": "llama3.2:3b", "size": "2.0 GB", "description": "Meta's Llama 3.2 3B compact model", "use_case": "Quick responses, low-resource devices"},
            {"name": "llama3.2:1b", "size": "1.3 GB", "description": "Meta's Llama 3.2 1B smallest model", "use_case": "Edge devices, minimal hardware"},
            {"name": "qwen2.5:72b", "size": "43 GB", "description": "Qwen 2.5 72B multilingual model", "use_case": "Multilingual tasks, translation, global content"},
            {"name": "qwen2.5:32b", "size": "20 GB", "description": "Qwen 2.5 32B model", "use_case": "Multilingual chat, balanced performance"},
            {"name": "qwen2.5:14b", "size": "9.0 GB", "description": "Qwen 2.5 14B model", "use_case": "General purpose, multilingual support"},
            {"name": "qwen2.5:7b", "size": "4.7 GB", "description": "Qwen 2.5 7B model", "use_case": "Fast multilingual responses"},
            {"name": "deepseek-r1:70b", "size": "43 GB", "description": "DeepSeek R1 70B reasoning model", "use_case": "Math, logic, scientific reasoning, complex problems"},
            {"name": "deepseek-r1:32b", "size": "20 GB", "description": "DeepSeek R1 32B reasoning model", "use_case": "Problem-solving, analytical tasks"},
            {"name": "deepseek-r1:14b", "size": "9.0 GB", "description": "DeepSeek R1 14B reasoning model", "use_case": "Reasoning tasks, balanced speed/quality"},
            {"name": "deepseek-r1:8b", "size": "4.9 GB", "description": "DeepSeek R1 8B reasoning model", "use_case": "Fast reasoning, logical queries"},
            {"name": "deepseek-r1:1.5b", "size": "1.1 GB", "description": "DeepSeek R1 1.5B compact model", "use_case": "Quick logic tasks, simple reasoning"},
            {"name": "mistral:7b", "size": "4.1 GB", "description": "Mistral 7B instruct model", "use_case": "General chat, instructions, writing"},
            {"name": "mixtral:8x7b", "size": "26 GB", "description": "Mixtral 8x7B mixture of experts", "use_case": "High-quality responses, diverse tasks"},
            {"name": "phi4:14b", "size": "8.7 GB", "description": "Microsoft Phi-4 14B model", "use_case": "STEM tasks, technical writing, reasoning"},
            {"name": "gemma2:27b", "size": "16 GB", "description": "Google's Gemma 2 27B model", "use_case": "High-quality chat, creative writing"},
            {"name": "gemma2:9b", "size": "5.5 GB", "description": "Google's Gemma 2 9B model", "use_case": "General purpose, good balance"},
            {"name": "gemma2:2b", "size": "1.6 GB", "description": "Google's Gemma 2 2B compact model", "use_case": "Quick tasks, limited resources"},
            {"name": "codestral:22b", "size": "13 GB", "description": "Mistral's code-specialized model", "use_case": "Code generation, debugging, programming"},
            {"name": "codegemma:7b", "size": "5.0 GB", "description": "Google's code-specialized Gemma", "use_case": "Code completion, small projects"},
            {"name": "llama3.2-vision:11b", "size": "7.9 GB", "description": "Llama 3.2 with vision capabilities", "use_case": "Image analysis, visual Q&A, OCR"},
            {"name": "llama3.2-vision:90b", "size": "55 GB", "description": "Llama 3.2 90B vision model", "use_case": "Advanced image understanding, multimodal"},
            {"name": "nomic-embed-text", "size": "274 MB", "description": "Text embedding model", "use_case": "Semantic search, text similarity, RAG"},
            {"name": "mxbai-embed-large", "size": "670 MB", "description": "Large embedding model", "use_case": "High-quality embeddings, vector databases"},
        ]

        self.create_widgets()
        self.refresh_installed_models()

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
        # Top frame with refresh button
        top_frame = ttk.Frame(self.installed_tab)
        top_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(top_frame, text="Refresh", command=self.refresh_installed_models).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Delete Selected", command=self.delete_model).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Show Model Info", command=self.show_model_info).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Configure for VS Code", command=self.configure_vscode).pack(side='left', padx=5)

        # Treeview for installed models
        columns = ('name', 'id', 'size', 'modified')
        self.installed_tree = ttk.Treeview(self.installed_tab, columns=columns, show='headings', height=20)

        self.installed_tree.heading('name', text='Model Name')
        self.installed_tree.heading('id', text='ID')
        self.installed_tree.heading('size', text='Size')
        self.installed_tree.heading('modified', text='Modified')

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

        ttk.Button(search_frame, text="Download Selected", command=self.download_model).pack(side='right', padx=5)

        # Treeview for catalog
        columns = ('name', 'size', 'use_case', 'description')
        self.catalog_tree = ttk.Treeview(self.catalog_tab, columns=columns, show='headings', height=25)

        self.catalog_tree.heading('name', text='Model Name')
        self.catalog_tree.heading('size', text='Size')
        self.catalog_tree.heading('use_case', text='Recommended For')
        self.catalog_tree.heading('description', text='Description')

        self.catalog_tree.column('name', width=200)
        self.catalog_tree.column('size', width=80)
        self.catalog_tree.column('use_case', width=280)
        self.catalog_tree.column('description', width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.catalog_tab, orient='vertical', command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)

        self.catalog_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

        # Populate catalog
        self.populate_catalog()

    def create_download_tab(self):
        # Progress text area
        self.progress_text = scrolledtext.ScrolledText(self.download_tab, wrap=tk.WORD, height=30)
        self.progress_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.download_tab)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Clear Log", command=self.clear_progress).pack(side='left', padx=5)

    def refresh_installed_models(self):
        # Clear existing items
        for item in self.installed_tree.get_children():
            self.installed_tree.delete(item)

        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
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
        for model in self.model_catalog:
            self.catalog_tree.insert('', 'end', values=(model['name'], model['size'], model['use_case'], model['description']))

    def filter_catalog(self, *args):
        search_term = self.search_var.get().lower()

        # Clear tree
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Repopulate with filtered results
        for model in self.model_catalog:
            if search_term in model['name'].lower() or search_term in model['description'].lower() or search_term in model['use_case'].lower():
                self.catalog_tree.insert('', 'end', values=(model['name'], model['size'], model['use_case'], model['description']))

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
            result = subprocess.run(['ollama', 'rm', model_name], capture_output=True, text=True, check=True)
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
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                self.log_progress(line)

            process.wait()

            if process.returncode == 0:
                self.log_progress(f"\n✓ Successfully downloaded: {model_name}\n")
                self.root.after(0, self.refresh_installed_models)
            else:
                self.log_progress(f"\n✗ Error downloading model (exit code: {process.returncode})\n")

        except Exception as e:
            self.log_progress(f"\n✗ Error: {str(e)}\n")

    def log_progress(self, message):
        def update():
            self.progress_text.insert(tk.END, message)
            self.progress_text.see(tk.END)
        self.root.after(0, update)

    def clear_progress(self):
        self.progress_text.delete(1.0, tk.END)

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


def main():
    root = tk.Tk()
    app = OllamaManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
