import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

def get_process_name(hwnd):
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    hProcess = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if hProcess:
        buf = ctypes.create_unicode_buffer(512)
        if psapi.GetModuleFileNameExW(hProcess, 0, buf, 512) > 0:
            kernel32.CloseHandle(hProcess)
            return buf.value.split('\\')[-1].lower()
        kernel32.CloseHandle(hProcess)
    return ""

def get_window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    return ""

def enum_windows_callback(hwnd, lParam):
    if user32.IsWindowVisible(hwnd):
        title = get_window_title(hwnd)
        if title:
            proc_name = get_process_name(hwnd)
            print(f"Title: '{title}' | Process: '{proc_name}'")
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
