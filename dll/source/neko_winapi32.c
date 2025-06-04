// neko_winapi.c
#include <windows.h>

// Move window to (x, y)
__declspec(dllexport) int move_window(HWND hwnd, int x, int y) {
    if (!hwnd) return -1;
    if (!SetWindowPos(hwnd, NULL, x, y, 0, 0, SWP_NOZORDER | SWP_NOSIZE | SWP_NOACTIVATE))
        return -2;
    return 0;
}

// Set window always on top (1 = yes, 0 = no)
__declspec(dllexport) int set_always_on_top(HWND hwnd, int enable) {
    if (!hwnd) return -1;
    if (!SetWindowPos(hwnd,
                      enable ? HWND_TOPMOST : HWND_NOTOPMOST,
                      0, 0, 0, 0,
                      SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE))
        return -2;
    return 0;
}

// Show (1) or hide (0) the window
__declspec(dllexport) int show_window(HWND hwnd, int show) {
    if (!hwnd) return -1;
    if (!ShowWindow(hwnd, show ? SW_SHOW : SW_HIDE))
        return -2;
    return 0;
}
