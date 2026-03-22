import sys
import pygetwindow as gw
import ctypes
from ctypes import wintypes
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3)
    ]

def capture_window_ctypes(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width <= 0 or height <= 0:
        return None

    hwndDC = user32.GetWindowDC(hwnd)
    mfcDC  = gdi32.CreateCompatibleDC(hwndDC)
    saveBitMap = gdi32.CreateCompatibleBitmap(hwndDC, width, height)
    gdi32.SelectObject(mfcDC, saveBitMap)

    # 2 = PW_RENDERFULLCONTENT
    result = user32.PrintWindow(hwnd, mfcDC, 2)
    
    if not result:
        user32.ReleaseDC(hwnd, hwndDC)
        gdi32.DeleteDC(mfcDC)
        gdi32.DeleteObject(saveBitMap)
        return None

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height # Top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0 # BI_RGB

    buffer = ctypes.create_string_buffer(width * height * 4)

    lines = gdi32.GetDIBits(mfcDC, saveBitMap, 0, height, buffer, ctypes.byref(bmi), 0)

    user32.ReleaseDC(hwnd, hwndDC)
    gdi32.DeleteDC(mfcDC)
    gdi32.DeleteObject(saveBitMap)

    if lines:
        try:
            image = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA', 0, 1)
            # Remove alpha channel if needed
            return image.convert('RGB')
        except Exception as e:
            print(f"PIL Error: {e}")
            return None
    return None

def main():
    windows = gw.getAllWindows()
    target = None
    for w in windows:
        if w.title and w.visible:
            target = w
            break

    if not target:
        print("No window found")
        return

    print(f"Capturing: {target.title}")
    img = capture_window_ctypes(target._hWnd)
    if img:
        img.save("test_out.png")
        print("Saved to test_out.png")
    else:
        print("Capture failed")

if __name__ == '__main__':
    main()
