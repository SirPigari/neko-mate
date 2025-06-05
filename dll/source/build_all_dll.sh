#!/usr/bin/env bash

# Check for compilers and install if missing
if ! command -v i686-w64-mingw32-gcc &> /dev/null; then
    echo "[INFO] 32-bit compiler not found. Installing..."
    pacman -S --noconfirm mingw-w64-i686-gcc || { echo "[FATAL] Failed to install 32-bit compiler"; exit 1; }
fi

if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    echo "[INFO] 64-bit compiler not found. Installing..."
    pacman -S --noconfirm mingw-w64-x86_64-gcc || { echo "[FATAL] Failed to install 64-bit compiler"; exit 1; }
fi

if [[ ":$PATH:" != *":/mingw32/bin:"* ]]; then
    export PATH="/mingw32/bin:$PATH"
    echo "[INFO] Added /mingw32/bin to current PATH"
fi

if [[ ":$PATH:" != *":/mingw64/bin:"* ]]; then
    export PATH="/mingw64/bin:$PATH"
    echo "[INFO] Added /mingw64/bin to current PATH"
fi

# 3. Add to ~/.bashrc permanently if not already there
add_path_to_bashrc() {
    local path_entry="$1"
    if ! grep -q "export PATH=.*$path_entry" ~/.bashrc 2>/dev/null; then
        echo "export PATH=\"$path_entry:\$PATH\"" >> ~/.bashrc
        echo "[INFO] Added $path_entry to ~/.bashrc"
    else
        echo "[INFO] $path_entry already in ~/.bashrc"
    fi
}

add_path_to_bashrc "/mingw32/bin"
add_path_to_bashrc "/mingw64/bin"

# Setup
cd ..
rm -f *.dll
mkdir -p ../debug

# Debug flags
CFLAGS="-g -O0 -Wall -Wextra -Wpedantic -v"

# neko_alpha
echo "Building neko_alpha DLLs..."

i686-w64-mingw32-gcc $CFLAGS -shared -o neko_alpha32.dll source/neko_alpha.c -lgdi32 > ../debug/build_alpha32.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_alpha32.dll. See debug/build_alpha32.log"
fi

x86_64-w64-mingw32-gcc $CFLAGS -shared -o neko_alpha64.dll source/neko_alpha.c -lgdi32 > ../debug/build_alpha64.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_alpha64.dll. See debug/build_alpha64.log"
fi

# neko_msgbox
echo "Building neko_msgbox DLLs..."

i686-w64-mingw32-gcc $CFLAGS -shared -o neko_msgbox32.dll source/neko_msgbox.c -lgdi32 > ../debug/build_msgbox32.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_msgbox32.dll. See debug/build_msgbox32.log"
fi

x86_64-w64-mingw32-gcc $CFLAGS -shared -o neko_msgbox64.dll source/neko_msgbox.c -lgdi32 > ../debug/build_msgbox64.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_msgbox64.dll. See debug/build_msgbox64.log"
fi

# neko_winapi
echo "Building neko_winapi DLLs..."

i686-w64-mingw32-gcc $CFLAGS -shared -o neko_winapi32.dll source/neko_winapi32.c -lgdi32 > ../debug/build_winapi32.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_winapi32.dll. See debug/build_winapi32.log"
fi

x86_64-w64-mingw32-gcc $CFLAGS -shared -o neko_winapi64.dll source/neko_winapi64.c -lgdi32 > ../debug/build_winapi64.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build neko_winapi64.dll. See debug/build_winapi64.log"
fi
