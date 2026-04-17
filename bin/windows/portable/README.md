# Windows Portable Executable

## Download

**ollama-manager-windows.exe** - Portable Windows executable (no installation!)

## Usage

1. Download `ollama-manager-windows.exe`
2. Place it anywhere (Desktop, Documents, USB drive, etc.)
3. Double-click to run
4. If Windows SmartScreen appears:
   - Click "More info"
   - Click "Run anyway"

## Create Desktop Shortcut (Optional)

1. Right-click the `.exe` file
2. Select "Send to" → "Desktop (create shortcut)"
3. Rename shortcut to "Ollama Manager"

Or pin to taskbar:
1. Right-click the `.exe` while running
2. Select "Pin to taskbar"

## System Requirements

- Windows 10 or later (64-bit)
- [Ollama](https://ollama.com/) installed

## File Info

- **Filename:** ollama-manager-windows.exe
- **Size:** 11 MB
- **Architecture:** x86_64
- **Type:** Portable executable (no Python or installation required)
- **SHA256:** `63cbc597b2aec4fc9a60e7734efd063dff2938ae5c97d357d8a24dd920d1d6f6`

## Why Portable?

✅ No installation required  
✅ No admin rights needed  
✅ Works from USB drives  
✅ Clean - just delete to uninstall  

## Verify Download

Check file integrity with PowerShell:
```powershell
Get-FileHash ollama-manager-windows.exe -Algorithm SHA256
```

Should match: `63cbc597b2aec4fc9a60e7734efd063dff2938ae5c97d357d8a24dd920d1d6f6`

## Building

To build this yourself, see [BUILD.md](../../../BUILD.md):

```bash
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py
```
