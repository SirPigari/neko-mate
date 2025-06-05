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

# Temporarily add to PATH
if [[ ":$PATH:" != *":/mingw32/bin:"* ]]; then
    export PATH="/mingw32/bin:$PATH"
    echo "[INFO] Added /mingw32/bin to current PATH"
fi

if [[ ":$PATH:" != *":/mingw64/bin:"* ]]; then
    export PATH="/mingw64/bin:$PATH"
    echo "[INFO] Added /mingw64/bin to current PATH"
fi

# Add permanently to ~/.bashrc
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

# Setup working directory
cd "$(dirname "$0")" || exit 1
cd .. || exit 1
rm -f ./*.dll
mkdir -p "debug"

# Debug flags
CFLAGS=( -g -O0 -Wall -Wextra -Wpedantic -v )

# Function to build a DLL
build_dll() {
    local compiler="$1"
    local output="$2"
    local source="$3"
    local log_file="$4"

    if "$compiler" "${CFLAGS[@]}" -shared -o "$output" "$source" -lgdi32 > "$log_file" 2>&1; then
        echo "[SUCCESS] Built $output"
    else
        echo "[ERROR] Failed to build $output. See $log_file"
    fi
}


echo "Building neko_alpha DLLs..."
build_dll "i686-w64-mingw32-gcc" "neko_alpha32.dll" "source/neko_alpha.c" "../debug/build_alpha32.log"
build_dll "x86_64-w64-mingw32-gcc" "neko_alpha64.dll" "source/neko_alpha.c" "../debug/build_alpha64.log"

echo "Building neko_msgbox DLLs..."
build_dll "i686-w64-mingw32-gcc" "neko_msgbox32.dll" "source/neko_msgbox.c" "../debug/build_msgbox32.log"
build_dll "x86_64-w64-mingw32-gcc" "neko_msgbox64.dll" "source/neko_msgbox.c" "../debug/build_msgbox64.log"

echo "Building neko_winapi DLLs..."
build_dll "i686-w64-mingw32-gcc" "neko_winapi32.dll" "source/neko_winapi.c" "../debug/build_winapi32.log"
build_dll "x86_64-w64-mingw32-gcc" "neko_winapi64.dll" "source/neko_winapi.c" "../debug/build_winapi64.log"
