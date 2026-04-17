# Building Linux Tarball

The Linux binary must be built on a Linux system for maximum compatibility.

## Quick Build (on Linux)

```bash
# Install PyInstaller
pip install pyinstaller

# Build the binary
pyinstaller --onefile --windowed --name "ollama-manager" ollama_manager.py

# Create versioned tarball
tar -czf ollama-manager-v1.0.0-linux-x64.tar.gz -C dist ollama-manager

# Generate checksum
sha256sum ollama-manager-v1.0.0-linux-x64.tar.gz

# Move to bin folder
mv ollama-manager-v1.0.0-linux-x64.tar.gz bin/linux/x64/
```

## Why Build on Linux?

- PyInstaller creates binaries for the OS it runs on
- Linux binaries built on Linux have better compatibility
- Recommended: Build on Ubuntu 20.04 for widest compatibility

## After Building

1. Update [CHECKSUMS.txt](../../CHECKSUMS.txt) with the SHA256 hash
2. Commit and push the tarball to the repository
3. Create a GitHub release with both Windows and Linux binaries

## Notes

- The tarball will be approximately 11-15 MB
- It will work on any modern Linux distro with glibc
- Users just extract and run - no installation needed
