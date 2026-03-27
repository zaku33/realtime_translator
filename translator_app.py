import tkinter as tk
import ctypes
import ctypes.wintypes
from tkinter import ttk
import mss
import mss.tools
import argostranslate.package
import argostranslate.translate
import asyncio
import threading
import time
from PIL import Image
import io
import pygetwindow as gw

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.wintypes.DWORD),
        ("biWidth", ctypes.wintypes.LONG),
        ("biHeight", ctypes.wintypes.LONG),
        ("biPlanes", ctypes.wintypes.WORD),
        ("biBitCount", ctypes.wintypes.WORD),
        ("biCompression", ctypes.wintypes.DWORD),
        ("biSizeImage", ctypes.wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.wintypes.LONG),
        ("biYPelsPerMeter", ctypes.wintypes.LONG),
        ("biClrUsed", ctypes.wintypes.DWORD),
        ("biClrImportant", ctypes.wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.wintypes.DWORD * 3)
    ]

class TranslatorOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Window Translator Control")
        
        # Initial small control window
        width = 400
        height = 190
        self.root.geometry(f"{width}x{height}")
        self.root.attributes('-topmost', True)
        
        # Native OCR is used natively
        
        # Offline Translation config
        self.status_label = tk.Label(control_frame, text="Ready", fg="blue", font=("Arial", 8))
        self.status_label.pack(side=tk.BOTTOM, anchor=tk.W, pady=(0, 2))
        
        # Variables and mapping
        self.lang_codes = {
            "Vietnamese": "vi", "English": "en", "Spanish": "es",
            "French": "fr", "Japanese": "ja", "Korean": "ko",
            "Chinese": "zh", "German": "de", "Italian": "it"
        }
        self.languages = list(self.lang_codes.keys())
        
        # Language Selection UI
        lang_frame = tk.Frame(control_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))

        # Source Language
        tk.Label(lang_frame, text="Source:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.source_var = tk.StringVar(value="English")
        self.source_dropdown = ttk.Combobox(lang_frame, textvariable=self.source_var, values=self.languages, state="readonly", width=12)
        self.source_dropdown.grid(row=0, column=1, padx=(5, 10))
        self.source_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        # Target Language
        tk.Label(lang_frame, text="Target:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky=tk.W)
        self.target_var = tk.StringVar(value="Vietnamese")
        self.target_dropdown = ttk.Combobox(lang_frame, textvariable=self.target_var, values=self.languages, state="readonly", width=12)
        self.target_dropdown.grid(row=0, column=3, padx=(5, 0))
        self.target_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Buttons
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.refresh_btn = tk.Button(btn_frame, text="Refresh Windows", command=self.refresh_windows)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_btn = tk.Button(btn_frame, text="Start Translating", command=self.start_translation, bg="green", fg="white")
        self.start_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.stop_btn = tk.Button(btn_frame, text="Stop", command=self.stop_translation, bg="red", fg="white", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT)
        
        tk.Label(control_frame, text="Note: Translating in-place over the selected window.", font=("Arial", 8, "italic"), fg="gray").pack(side=tk.BOTTOM, pady=(10, 0))

        # Initial population of windows
        self.refresh_windows()

        # State Variables
        self.running = False
        self.target_window_title = ""
        self.overlay_window = None
        self.text_labels = []   # Store dynamic labels here
        self.translation_cache = {} # Cache translated texts
        self.capture_thread = None

    def refresh_windows(self):
        valid_windows = []
        
        system_procs = {
            'explorer.exe', 'applicationframehost.exe', 'systemsettings.exe', 
            'textinputhost.exe', 'searchapp.exe', 'searchhost.exe', 
            'shellexperiencehost.exe', 'taskmgr.exe'
        }

        def get_process_name(hwnd):
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
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
            user32 = ctypes.windll.user32
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value
            return ""

        def enum_windows_callback(hwnd, lParam):
            user32 = ctypes.windll.user32
            if user32.IsWindowVisible(hwnd):
                title = get_window_title(hwnd)
                if title and title != "Window Translator Control" and title != "Program Manager":
                    proc_name = get_process_name(hwnd)
                    if proc_name not in system_procs:
                        valid_windows.append(title)
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

        unique_windows = list(dict.fromkeys(valid_windows))
        self.window_dropdown['values'] = unique_windows
        if unique_windows:
            self.window_dropdown.current(0)
        else:
            self.window_dropdown.set('')

    def on_language_change(self, event):
        # Clear cache when language changes
        self.translation_cache.clear()
        # Optionally, clear overlay to force re-translate immediately
        self.clear_overlay()

    def start_translation(self):
        selected = self.window_var.get()
        if not selected:
            return
            
        self.target_window_title = selected
        self.running = True
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.window_dropdown.config(state=tk.DISABLED)
        self.refresh_btn.config(state=tk.DISABLED)
        
        # Create transparent overlay window
        self.create_overlay()
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()

    def stop_translation(self):
        self.running = False
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.window_dropdown.config(state="readonly")
        self.refresh_btn.config(state=tk.NORMAL)
        
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
            self.text_labels = []

    def create_overlay(self):
        if self.overlay_window:
            self.overlay_window.destroy()
            
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("Translation Overlay")
        self.overlay_window.attributes('-topmost', True)
        
        # Make transparent and click-through
        transparent_color = 'magenta'
        self.overlay_window.wm_attributes('-transparentcolor', transparent_color)
        self.overlay_window.configure(bg=transparent_color)
        
        # Remove borders
        self.overlay_window.overrideredirect(True)
        
        # Initial position updates soon in loop
        self.overlay_window.geometry("10x10+0+0")
        
    def clear_overlay(self):
        # Remove all existing labels
        for label in self.text_labels:
            label.destroy()
        self.text_labels = []

    def update_overlay_geometry(self, win):
        """ Update the position and size of the transparent overlay to match the target window """
        if not self.overlay_window or not self.running:
            return False
            
        try:
            # Add a slight offset to avoid capturing window borders if needed, but for simplicity:
            x, y, w, h = win.left, win.top, win.width, win.height
            
            # Simple check if window is minimized (usually coordinates are way off or sizes are 0)
            if w <= 0 or h <= 0 or x < -32000:
                self.overlay_window.geometry("0x0+0+0")
                return False

            self.overlay_window.geometry(f"{w}x{h}+{x}+{y}")
            return True
        except Exception:
            return False

    def draw_translated_text(self, box, text):
        """ Draw translated text exactly where the original text was """
        if not self.overlay_window or not self.running:
            return
            
        # Box format from easyocr: [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        # We need top-left coordinates and width/height
        top_left = box[0]
        bottom_right = box[2]
        
        x = int(top_left[0])
        y = int(top_left[1])
        w = int(bottom_right[0] - top_left[0])
        h = int(bottom_right[1] - top_left[1])
        
        # Create a label with yellow text on black background for visibility
        label = tk.Label(self.overlay_window, text=text, bg="black", fg="yellow", 
                         font=("Arial", max(8, int(h * 0.7))), # Try to scale font size to bounding box height
                         wraplength=w, justify="left", 
                         highlightthickness=0, borderwidth=0)
        
        # Place it at the coordinates relative to the overlay window
        label.place(x=x, y=y, width=w, height=h)
        self.text_labels.append(label)

    def capture_window_image(self, hwnd, width, height):
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        hwndDC = user32.GetWindowDC(hwnd)
        mfcDC  = gdi32.CreateCompatibleDC(hwndDC)
        saveBitMap = gdi32.CreateCompatibleBitmap(hwndDC, width, height)
        gdi32.SelectObject(mfcDC, saveBitMap)

        # PW_RENDERFULLCONTENT = 2
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
        bmi.bmiHeader.biCompression = 0

        buffer = ctypes.create_string_buffer(width * height * 4)
        gdi32.GetDIBits(mfcDC, saveBitMap, 0, height, buffer, ctypes.byref(bmi), 0)

        user32.ReleaseDC(hwnd, hwndDC)
        gdi32.DeleteDC(mfcDC)
        gdi32.DeleteObject(saveBitMap)

        try:
            image = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA', 0, 1)
            return image.convert('RGB')
        except Exception as e:
            print(f"PIL Error: {e}")
            return None

    def capture_loop(self):
        while self.running:
            try:
                # Find target window
                try:
                    windows = gw.getWindowsWithTitle(self.target_window_title)
                    if not windows:
                        print(f"Window '{self.target_window_title}' not found.")
                        time.sleep(2)
                        continue
                    win = windows[0]
                except Exception as e:
                    print(f"Window search error: {e}")
                    time.sleep(2)
                    continue

                # Important: Update overlay to follow the target window
                if not self.update_overlay_geometry(win):
                    time.sleep(1)
                    continue
                    
                x, y, w, h = win.left, win.top, win.width, win.height
                
                if w <= 0 or h <= 0:
                    continue
                    
                target_image = self.capture_window_image(win._hWnd, w, h)
                if not target_image:
                    print("Failed to capture specific window, it might be minimized or hardware-accelerated.")
                    time.sleep(1)
                    continue
                
                # Convert to bytes for easyocr
                img_byte_arr = io.BytesIO()
                target_image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Run OCR
                results = self.perform_ocr_sync(img_bytes)
                
                # Process results main thread
                self.root.after(0, self.process_ocr_results, results)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                
            time.sleep(3) # Throttle to prevent system overload and unnecessary translation

    def perform_ocr_sync(self, img_bytes):
        return asyncio.run(self.perform_ocr_async(img_bytes))

    async def perform_ocr_async(self, img_bytes):
        try:
            from winrt.windows.media.ocr import OcrEngine
            from winrt.windows.globalization import Language
            from winrt.windows.graphics.imaging import BitmapDecoder
            from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream
            
            stream = InMemoryRandomAccessStream()
            writer = DataWriter(stream)
            writer.write_bytes(bytearray(img_bytes))
            await writer.store_async()
            stream.seek(0)
            
            decoder = await BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            
            engine = OcrEngine.try_create_from_user_profile_languages()
            if not engine:
                engine = OcrEngine.try_create_from_language(Language("en-US"))
                
            result = await engine.recognize_async(bitmap)
            res = []
            if result:
                for line in result.lines:
                    if not line.words: continue
                    min_x = min(w.bounding_rect.x for w in line.words)
                    min_y = min(w.bounding_rect.y for w in line.words)
                    max_x = max(w.bounding_rect.x + w.bounding_rect.width for w in line.words)
                    max_y = max(w.bounding_rect.y + w.bounding_rect.height for w in line.words)
                    bbox = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
                    res.append((bbox, line.text, 1.0))
            return res
        except Exception as e:
            print(f"Native OCR error: {e}")
            return []

    def process_ocr_results(self, results):
        if not self.running or not self.overlay_window:
            return
            
        self.clear_overlay()
        
        for (bbox, text, prob) in results:
            if prob < 0.2 or not text.strip():
                continue
                
            text = text.strip()
            # Basic validation to skip very short mostly noise strings
            if len(text) < 2 and not text.isalnum():
                continue
                
            # Check cache first
            if text in self.translation_cache:
                translated = self.translation_cache[text]
                self.draw_translated_text(bbox, translated)
            else:
                # Need to translate
                # To avoid blocking the UI, translation should ideally be asynchronous,
                # but for simplicity let's spin up a quick daemon thread per block
                threading.Thread(target=self.translate_and_draw_async, args=(bbox, text), daemon=True).start()

    def translate_and_draw_async(self, bbox, orig_text):
        translated = self.translate_text(orig_text)
        if translated and not translated.startswith("Error"):
            self.translation_cache[orig_text] = translated
            if self.running:
                self.root.after(0, self.draw_translated_text, bbox, translated)

    def ensure_model_installed(self, from_code, to_code):
        installed_languages = argostranslate.translate.get_installed_languages()
        
        from_lang = next((l for l in installed_languages if l.code == from_code), None)
        to_lang = next((l for l in installed_languages if l.code == to_code), None)

        if from_lang and to_lang and from_lang.get_translation(to_lang):
            return True

        self.root.after(0, lambda: self.status_label.config(text=f"Downloading {from_code}->{to_code} model..."))
        try:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
                ), None
            )
            if package_to_install:
                argostranslate.package.install_from_path(package_to_install.download())
                self.root.after(0, lambda: self.status_label.config(text="Model installed! Ready."))
                return True
            else:
                self.root.after(0, lambda: self.status_label.config(text=f"Model {from_code}->{to_code} not found!"))
                return False
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Error downloading model: {e}"))
            return False

    def translate_text(self, text):
        from_lang = self.source_var.get()
        to_lang = self.target_var.get()
        
        if from_lang == to_lang:
            return text
            
        from_code = self.lang_codes.get(from_lang, "en")
        to_code = self.lang_codes.get(to_lang, "vi")
        
        if not self.ensure_model_installed(from_code, to_code):
            return "Error: Language pair not supported or failed to download."
            
        try:
            translated_text = argostranslate.translate.translate(text, from_code, to_code)
            return translated_text
        except Exception as e:
            return f"Error: {str(e)}"

    def stop(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorOverlay(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
