#include <windows.h>

__declspec(dllexport)
void* get_hwnd(const char* title) {
    if (!title) return NULL;
    return FindWindowA(NULL, title);
}

__declspec(dllexport)
int move_window(void* hwnd, int x, int y) {
    if (!hwnd) return 0;
    return SetWindowPos((HWND)hwnd, NULL, x, y, 0, 0, SWP_NOZORDER | SWP_NOSIZE | SWP_NOACTIVATE) ? 1 : 0;
}

__declspec(dllexport)
int set_always_on_top(void* hwnd, int enable) {
    if (!hwnd) return 0;
    return SetWindowPos((HWND)hwnd,
                        enable ? HWND_TOPMOST : HWND_NOTOPMOST,
                        0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE) ? 1 : 0;
}

__declspec(dllexport)
int show_window(void* hwnd, int cmd) {
    if (!hwnd) return 0;
    return ShowWindow((HWND)hwnd, cmd) ? 1 : 0;
}
