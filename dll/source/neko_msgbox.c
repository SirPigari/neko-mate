#include <windows.h>

// __declspec(dllexport) makes it available outside the DLL
__declspec(dllexport)
int show_msgbox(const char* title, const char* message, int flags) {
    return MessageBoxA(NULL, message, title, flags);
}
