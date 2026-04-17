# Building Ollama Manager - Portable Executables

Build standalone, portable executables that require no installation.

## Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

## Quick Build

### Windows
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```
Output: `dist/ollama-manager.exe` (~11 MB)

### Linux
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
chmod +x dist/ollama-manager
tar -czf ollama-manager-linux-x64.tar.gz -C dist ollama-manager
```
Output: `ollama-manager-linux-x64.tar.gz`

### macOS
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```
Output: `dist/ollama-manager.app`

---

## Platform Details

### Windows Build

**Build command:**
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```

**What it does:**
- `--onefile`: Single executable (no DLLs or folders)
- `--windowed`: No console window (GUI-only)
- `--name`: Output filename

**Result:** Portable `.exe` file that runs on any Windows 10/11 (x64) system.

**To distribute:**
```bash
# Optional: Rename for clarity
mv dist/ollama-manager.exe dist/ollama-manager-windows.exe

# Generate checksum
sha256sum dist/ollama-manager-windows.exe
```

---

### Linux Build

**Requirements:**
- Build on Linux for Linux (cross-compilation is complex)
- PyInstaller installed

**Build command:**
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
chmod +x dist/ollama-manager
```

**Create tarball for distribution:**
```bash
tar -czf ollama-manager-linux-x64.tar.gz -C dist ollama-manager
```

**Result:** Portable binary that works on any modern Linux distro with glibc.

**To distribute:**
```bash
# Generate checksum
sha256sum ollama-manager-linux-x64.tar.gz
```

---

### macOS Build

**Requirements:**
- Build on macOS for macOS
- PyInstaller installed

**Build command:**
```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```

**Result:** `dist/ollama-manager.app` bundle (portable, works on Intel & Apple Silicon)

**To distribute:**
```bash
# Option 1: Zip it
cd dist
zip -r ollama-manager-macos.zip ollama-manager.app

# Option 2: Create DMG (requires create-dmg)
brew install create-dmg
create-dmg \
  --volname "Ollama Manager" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  ollama-manager-macos.dmg \
  dist/ollama-manager.app
```

---

## Build Options

### Reduce File Size

Add `--strip` to remove debug symbols:
```bash
pyinstaller --onefile --windowed --strip --name "ollama-manager" ollama_manager.py
```

### Add Custom Icon

```bash
# Windows
pyinstaller --onefile --windowed --icon=icon.ico --name "ollama-manager" ollama_manager.py

# macOS
pyinstaller --onefile --windowed --icon=icon.icns --name "ollama-manager" ollama_manager.py

# Linux (icon not embedded in binary)
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```

### Debug Build Issues

Remove `--windowed` to see console output:
```bash
pyinstaller --onefile --name "ollama-manager" ollama_manager.py
```

---

## Troubleshooting

### Windows: Large file size
- Normal range: 10-15 MB (includes Python runtime and tkinter)
- Use `--strip` flag to reduce size slightly
- PyInstaller bundles all dependencies - this is expected

### Linux: Binary won't run on other distros
- Ensure you're building on an older/common distro (Ubuntu 20.04 recommended)
- Check glibc version compatibility
- Test on multiple distros before distributing

### macOS: "App is damaged"
```bash
xattr -cr dist/ollama-manager.app
```

### All Platforms: Import errors
- PyInstaller should auto-detect tkinter
- If issues occur, add: `--hidden-import tkinter`

---

## Distribution Checklist

Before releasing binaries:

1. **Build on each platform**
   - Windows: Build on Windows
   - Linux: Build on Linux (Ubuntu 20.04 recommended for compatibility)
   - macOS: Build on macOS

2. **Test on clean systems**
   - Test on systems without Python installed
   - Verify Ollama integration works
   - Test all features (download, delete, VS Code config)

3. **Generate checksums**
   ```bash
   # Windows (PowerShell)
   Get-FileHash ollama-manager-windows.exe -Algorithm SHA256
   
   # Linux/macOS
   sha256sum ollama-manager-linux-x64.tar.gz
   sha256sum ollama-manager-macos.zip
   ```

4. **Update version**
   - Update `__version__` in `ollama_manager.py`
   - Update README files with new checksums
   - Update CHECKSUMS.txt

5. **Create GitHub release**
   - Tag format: `v1.0.0`
   - Attach binaries
   - Include checksums in release notes

---

## CI/CD (GitHub Actions)

Automate builds with GitHub Actions:

```yaml
name: Build Releases

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
      - run: mv dist/ollama-manager.exe dist/ollama-manager-windows.exe
      - uses: actions/upload-artifact@v3
        with:
          name: windows-binary
          path: dist/ollama-manager-windows.exe

  build-linux:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
      - run: chmod +x dist/ollama-manager
      - run: tar -czf ollama-manager-linux-x64.tar.gz -C dist ollama-manager
      - uses: actions/upload-artifact@v3
        with:
          name: linux-binary
          path: ollama-manager-linux-x64.tar.gz

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
      - run: cd dist && zip -r ollama-manager-macos.zip ollama-manager.app
      - uses: actions/upload-artifact@v3
        with:
          name: macos-binary
          path: dist/ollama-manager-macos.zip
```

---

## Why Portable?

✅ **No installation** - Just download and run  
✅ **No admin rights** - Works from any folder  
✅ **USB-friendly** - Run from external drives  
✅ **Clean removal** - Just delete the file  
✅ **Multiple versions** - Run different versions side-by-side  
✅ **Cross-platform** - Same approach for all OSes

---

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Python tkinter](https://docs.python.org/3/library/tkinter.html)
- [Ollama Documentation](https://github.com/ollama/ollama)
