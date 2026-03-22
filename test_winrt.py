import asyncio
import io
import mss
from PIL import Image

try:
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream
except ImportError as e:
    print(f"Failed to import winrt components: {e}")
    exit(1)

async def recognize_mss():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
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
            
            if result:
                print("Text lines:")
                for line in result.lines:
                    min_x = min([w.bounding_rect.x for w in line.words]) if line.words else 0
                    min_y = min([w.bounding_rect.y for w in line.words]) if line.words else 0
                    print(f"[{min_x}, {min_y}] {line.text}")
                    break
            else:
                print("No text recognized.")
            
            print("winrt OCR worked perfectly.")
            return True
    except Exception as e:
        print(f"Error executing winsdk OCR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(recognize_mss())
