# Linux Portable Binary

## Download

**ollama-manager-v*.*.*-linux-x64.tar.gz** - Portable Linux executable

**Current version:** `ollama-manager-v1.0.0-linux-x64.tar.gz` (to be built)

## Usage

```bash
# Extract
tar -xzf ollama-manager-v*.*.*-linux-x64.tar.gz

# Make executable
chmod +x ollama-manager

# Run
./ollama-manager
```

That's it! No installation required.

## Create Desktop Shortcut (Optional)

```bash
# Copy to user binaries (no sudo needed)
mkdir -p ~/.local/bin
cp ollama-manager ~/.local/bin/

# Create desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/ollama-manager.desktop <<DESKTOP
[Desktop Entry]
Type=Application
Name=Ollama Manager
Comment=Manage Ollama AI Models - Portable
Exec=$HOME/.local/bin/ollama-manager
Terminal=false
Categories=Utility;Development;
DESKTOP
```

## System Requirements

- Any modern Linux distribution (glibc-based)
- [Ollama](https://ollama.com/) installed
- x86_64 architecture

## File Info

- **Filename pattern:** `ollama-manager-v*.*.*-linux-x64.tar.gz`
- **Current version:** v1.0.0 (to be built)
- **Type:** Portable binary (no installation required)
- **Architecture:** x86_64
- **Size:** ~11-15 MB

## Why Portable?

✅ No package manager needed  
✅ No root/sudo required  
✅ Works on any distro  
✅ USB-friendly  
✅ Clean - just delete to uninstall  

## Compatible Distros

Works on any Linux with glibc:
- Ubuntu/Debian/Mint
- Fedora/RHEL/CentOS
- Arch Linux/Manjaro
- openSUSE
- Pop!_OS
- And virtually all others

## Verify Download

```bash
sha256sum ollama-manager-v*.*.*-linux-x64.tar.gz
```

Compare with checksum in [CHECKSUMS.txt](../../CHECKSUMS.txt)

## Building

Build on a Linux machine - see [BUILD.md](../../../BUILD.md):

```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
tar -czf ollama-manager-v1.0.0-linux-x64.tar.gz -C dist ollama-manager
```
