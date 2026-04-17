# Ollama Model Manager

A graphical interface to manage local Ollama models and browse/download from the model library.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### 📦 Installed Models Management
- View all installed Ollama models with details (name, ID, size, last modified)
- Delete models you no longer need
- Show detailed model information (format, family, parameter size, quantization)
- Quick refresh to see updated model list

### 📚 Model Catalog
- Browse 24+ curated popular models (Llama, Qwen, DeepSeek, Mistral, Gemma, etc.)
- Search functionality across model names, descriptions, and use cases
- See recommended use cases for each model:
  - **Reasoning**: DeepSeek R1 series for math, logic, scientific problems
  - **Multilingual**: Qwen models for translation and global content
  - **Coding**: Codestral and CodeGemma for programming tasks
  - **Vision**: Llama Vision models for image analysis
  - **Embeddings**: Nomic and MXBai for semantic search and RAG

### 🔧 Custom Model Download
- Download any model by name or URL
- Supports:
  - Standard models: `llama3:8b`
  - User models: `username/modelname`
  - Registry URLs

### 📊 Real-time Progress
- Live download progress tracking
- Detailed logging for all operations
- Background threading keeps UI responsive

### 🔌 VS Code Integration
- One-click configuration for VS Code chat extensions
- Support for:
  - **Continue** extension (with auto-complete)
  - **Ollama** extension
  - Manual settings.json configuration
- Quick copy buttons for model names and configs
- Direct access to VS Code settings folder

## Prerequisites

- Python 3.7 or higher
- [Ollama](https://ollama.com/) installed and running
- tkinter (usually included with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ollama-manager.git
cd ollama-manager
```

2. Make sure Ollama is installed and running:
```bash
ollama --version
```

3. Run the application:
```bash
python ollama_manager.py
```

## Building Standalone Executables

You can create standalone executables for Windows, Linux, and macOS using PyInstaller.

### Prerequisites for Building

Install PyInstaller:
```bash
pip install pyinstaller
```

### Windows Build

Build a standalone Windows executable:
```bash
pyinstaller --onefile --windowed --name "OllamaManager" --icon=icon.ico ollama_manager.py
```

The executable will be in `dist/OllamaManager.exe`

**Options:**
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (GUI-only)
- `--name`: Sets the executable name
- `--icon`: Adds a custom icon (optional, requires icon.ico file)

**To run:**
```bash
dist\OllamaManager.exe
```

### Linux Build

Build for Linux:
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```

The executable will be in `dist/ollama-manager`

**Make it executable:**
```bash
chmod +x dist/ollama-manager
```

**To run:**
```bash
./dist/ollama-manager
```

**Optional: Create a desktop entry** (`~/.local/share/applications/ollama-manager.desktop`):
```ini
[Desktop Entry]
Type=Application
Name=Ollama Manager
Comment=Manage Ollama AI Models
Exec=/path/to/dist/ollama-manager
Icon=/path/to/icon.png
Terminal=false
Categories=Utility;Development;
```

### macOS Build

Build for macOS:
```bash
pyinstaller --onefile --windowed --name "OllamaManager" ollama_manager.py
```

The app bundle will be in `dist/OllamaManager.app`

**To run:**
```bash
open dist/OllamaManager.app
```

Or double-click the app in Finder.

**Note:** On macOS Catalina and later, you may need to allow the app in System Preferences > Security & Privacy.

**To create a .dmg installer (optional):**
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Ollama Manager" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "OllamaManager.dmg" \
  "dist/OllamaManager.app"
```

### Cross-Platform Build Tips

**Reduce executable size:**
```bash
pyinstaller --onefile --windowed --strip --name "OllamaManager" ollama_manager.py
```

**Include additional files (if needed):**
```bash
pyinstaller --onefile --windowed --add-data "README.md:." --name "OllamaManager" ollama_manager.py
```

**Debug build issues:**
```bash
# Run without --windowed to see console output
pyinstaller --onefile --name "OllamaManager" ollama_manager.py
```

**Build for distribution:**
1. Test the executable on a clean system without Python installed
2. For Windows: Consider code signing to avoid SmartScreen warnings
3. For macOS: Consider notarization for distribution outside App Store
4. For Linux: Test on multiple distributions (Ubuntu, Fedora, etc.)

### Build Troubleshooting

**Windows: "Failed to execute script"**
- Remove `--windowed` flag to see error messages
- Check antivirus hasn't quarantined the exe

**Linux: "cannot execute binary file"**
- Ensure you built on the same architecture (x64/ARM)
- Verify executable permissions with `chmod +x`

**macOS: "App is damaged and can't be opened"**
- Run: `xattr -cr dist/OllamaManager.app`
- This removes quarantine attributes

**All Platforms: Large executable size**
- PyInstaller bundles Python and dependencies (~50-100 MB is normal)
- Use `--strip` flag to reduce size
- Consider UPX compression (add `--upx-dir` flag)

## Usage

### Managing Installed Models

1. **View Models**: The "Installed Models" tab shows all your current models
2. **Refresh**: Click "Refresh" to update the list
3. **Delete**: Select a model and click "Delete Selected" to remove it
4. **Info**: Select a model and click "Show Model Info" for technical details
5. **VS Code**: Select a model and click "Configure for VS Code" to set it up in VS Code

### Downloading Models

**From Catalog:**
1. Go to the "Model Catalog" tab
2. Browse or search for a model
3. Select it and click "Download Selected"

**Custom Model:**
1. Go to the "Model Catalog" tab
2. Enter the model name in the "Custom Model" field
3. Examples:
   - `llama3:8b`
   - `deepseek-r1:14b`
   - `username/custom-model`
4. Click "Download"

### Monitoring Progress

- Switch to the "Download Progress" tab to see real-time logs
- Downloads run in the background
- The installed models list auto-refreshes after successful downloads

## Model Recommendations

| Use Case | Recommended Models | Size |
|----------|-------------------|------|
| **Complex Reasoning** | deepseek-r1:70b, llama3.3:70b | 43+ GB |
| **Balanced Performance** | qwen2.5:14b, phi4:14b | 8-9 GB |
| **Fast Responses** | llama3.2:3b, gemma2:2b | 1-2 GB |
| **Coding** | codestral:22b, codegemma:7b | 5-13 GB |
| **Multilingual** | qwen2.5 series | 4-43 GB |
| **Vision/Images** | llama3.2-vision:11b | 8+ GB |
| **Embeddings/RAG** | nomic-embed-text | 274 MB |

## Technical Details

- **GUI Framework**: tkinter (cross-platform)
- **Ollama Integration**: 
  - CLI for model operations (`ollama list`, `ollama pull`, `ollama rm`)
  - REST API for model details (`http://localhost:11434/api/*`)
- **Threading**: Background operations prevent UI freezing
- **No External Dependencies**: Uses only Python standard library

## Troubleshooting

**"Ollama CLI not found"**
- Make sure Ollama is installed: https://ollama.com/
- Verify it's in your PATH: `ollama --version`

**"Failed to list models"**
- Check if Ollama service is running
- Try: `ollama serve` (in a separate terminal)

**Download stuck or slow**
- Large models take time (70B models are 40+ GB)
- Check your internet connection
- Check the "Download Progress" tab for details

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Add more models to the catalog

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built for [Ollama](https://ollama.com/)
- Model information curated from the Ollama library
- Uses Python's built-in tkinter for cross-platform compatibility
- Developed with assistance from AI models: Claude (Anthropic), Qwen, and Codestral
