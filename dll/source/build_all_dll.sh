cd ..

rm *.dll
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
