# Ollama Manager - Portable Binaries

**Portable executables** for Ollama Manager v1.0.0 - No installation required!

## What is Portable?

These are **standalone executables** - just download and run. No installation, no admin rights needed. Perfect for USB drives or temporary setups.

## Download

### Windows (Portable)
- **File:** [`ollama-manager-windows.exe`](windows/portable/ollama-manager-windows.exe)
- **Size:** 11 MB
- **Runs on:** Windows 10/11 (x64)

### Linux (Portable)
- **File:** `ollama-manager-linux-x64.tar.gz` *(build required - see below)*
- **Runs on:** Any modern Linux distro (x64)

### macOS
- **Build required on macOS** - See [BUILD.md](../BUILD.md)

## Quick Start

### Windows

1. Download [`ollama-manager-windows.exe`](windows/portable/ollama-manager-windows.exe)
2. Double-click to run
3. If SmartScreen appears: Click "More info" → "Run anyway"

**Optional:** Create a shortcut on your desktop or taskbar for easy access.

### Linux

1. Download `ollama-manager-linux-x64.tar.gz`
2. Extract and run:
```bash
tar -xzf ollama-manager-linux-x64.tar.gz
chmod +x ollama-manager
./ollama-manager
```

**Optional:** Create a desktop shortcut:
```bash
# Copy to user binaries (no sudo needed)
mkdir -p ~/.local/bin
cp ollama-manager ~/.local/bin/

# Create desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/ollama-manager.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Ollama Manager
Comment=Manage Ollama AI Models
Exec=$HOME/.local/bin/ollama-manager
Terminal=false
Categories=Utility;Development;
EOF
```

## File Verification (SHA256)

```
63cbc597b2aec4fc9a60e7734efd063dff2938ae5c97d357d8a24dd920d1d6f6  ollama-manager-windows.exe
```

**Verify on Windows (PowerShell):**
```powershell
Get-FileHash ollama-manager-windows.exe -Algorithm SHA256
```

**Verify on Linux:**
```bash
sha256sum ollama-manager-linux-x64.tar.gz
```

## System Requirements

- **Disk:** ~11-15 MB per executable
- **RAM:** ~50-100 MB when running
- **Prerequisites:** [Ollama](https://ollama.com/) must be installed
- **Internet:** Required for downloading models

## Building Other Platforms

This repository currently includes pre-built Windows binaries. For other platforms:

**Linux:** Build on Linux machine
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
tar -czf ollama-manager-linux-x64.tar.gz dist/ollama-manager
```

**macOS:** Build on macOS machine
```bash
pyinstaller --onefile --windowed --name "OllamaManager" ollama_manager.py
# The .app bundle is portable - just zip it or create a DMG
```

See [BUILD.md](../BUILD.md) for detailed build instructions.

## Why Portable?

✅ **No installation** - Just download and run  
✅ **No admin rights** - Works from any folder  
✅ **USB-friendly** - Run from external drives  
✅ **Clean uninstall** - Just delete the file  
✅ **Multiple versions** - Run different versions side-by-side  

## Troubleshooting

**Windows: "Windows protected your PC"**
- Click "More info" → "Run anyway"
- Binary is not code-signed (safe to run)

**Linux: Permission denied**
```bash
chmod +x ollama-manager
```

**Ollama not detected**
- Install Ollama: https://ollama.com/
- Verify: `ollama --version`

## Version History

- **v1.0.0** (2026-04-17) - Initial portable release

## License

MIT License - see [LICENSE](../LICENSE) file for details
