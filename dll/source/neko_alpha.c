#include <windows.h>
#include <stdint.h>

__declspec(dllexport)
void process_pixels_premult_rotate_flip(const uint8_t* input_data, int width, int height, uint8_t* output_data) {
    int new_width = height;
    int new_height = width;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int src_index = (y * width + x) * 4;
            uint8_t b = input_data[src_index + 0];
            uint8_t g = input_data[src_index + 1];
            uint8_t r = input_data[src_index + 2];
            uint8_t a = input_data[src_index + 3];

            // Premultiply RGB by alpha
            uint16_t r_p = (r * a) / 255;
            uint16_t g_p = (g * a) / 255;
            uint16_t b_p = (b * a) / 255;

            // Calculate dst pixel with rotation 90° CCW + vertical flip
            int dst_x = y;
            int dst_y = width - 1 - x;
            int dst_index = (dst_y * new_width + dst_x) * 4;

            output_data[dst_index + 0] = (uint8_t)b_p;
            output_data[dst_index + 1] = (uint8_t)g_p;
            output_data[dst_index + 2] = (uint8_t)r_p;
            output_data[dst_index + 3] = a;
        }
    }
}

__declspec(dllexport)
int update_layered_window(HWND hwnd, unsigned char* pixel_data, int width, int height) {
    if (!hwnd || !pixel_data || width <= 0 || height <= 0) return 0;

    // Get current extended style
    LONG exStyle = GetWindowLong(hwnd, GWL_EXSTYLE);

    // Set layered, hide from taskbar by adding toolwindow and removing appwindow
    exStyle |= WS_EX_LAYERED | WS_EX_TOOLWINDOW;
    exStyle &= ~WS_EX_APPWINDOW;
    SetWindowLong(hwnd, GWL_EXSTYLE, exStyle);

    // Set desktop as owner to hide from taskbar
    SetWindowLongPtr(hwnd, GWLP_HWNDPARENT, (LONG_PTR)GetDesktopWindow());

    // Apply style changes without activating window
    SetWindowPos(hwnd, NULL, 0, 0, 0, 0,
                 SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_NOACTIVATE);

    HDC hdcScreen = GetDC(NULL);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);

    BITMAPINFO bmi = { 0 };
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = width;
    bmi.bmiHeader.biHeight = height;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    void* bits = NULL;
    HBITMAP hBitmap = CreateDIBSection(hdcMem, &bmi, DIB_RGB_COLORS, &bits, NULL, 0);
    if (!hBitmap) {
        DeleteDC(hdcMem);
        ReleaseDC(NULL, hdcScreen);
        return 0;
    }

    // Clear bits to zero to avoid junk pixels
    memset(bits, 0, width * height * 4);

    // Copy pixel data (assumed BGRA format)
    SetDIBits(hdcMem, hBitmap, 0, height, pixel_data, &bmi, DIB_RGB_COLORS);


    HBITMAP hOldBitmap = (HBITMAP)SelectObject(hdcMem, hBitmap);

    SIZE size = { width, height };
    POINT ptSrc = { 0, 0 };
    RECT rect;
    GetWindowRect(hwnd, &rect);
    POINT ptDst = { rect.left, rect.top };

    BLENDFUNCTION blend = { AC_SRC_OVER, 0, 255, AC_SRC_ALPHA };
    GdiFlush(); // after the call to UpdateLayeredWindow


    BOOL result = UpdateLayeredWindow(hwnd, hdcScreen, &ptDst, &size, hdcMem, &ptSrc, 0, &blend, ULW_ALPHA);

    SelectObject(hdcMem, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(NULL, hdcScreen);

    return result ? 1 : 0;
}
