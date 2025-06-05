#include <windows.h>

__declspec(dllexport)
int show_msgbox(const char* title, const char* message, int flags) {
    return MessageBoxA(NULL, message, title, flags);
}

__declspec(dllexport)
int show_msgbox_w(const wchar_t* title, const wchar_t* message, int flags) {
    return MessageBoxW(NULL, message, title, flags);
}