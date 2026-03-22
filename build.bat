@echo off
echo Installing PyInstaller and required dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Cleaning up old builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

echo.
echo Building executable (this should be much faster now without easyocr)...
pyinstaller --clean --noconfirm --onedir --windowed --name "RealtimeTranslator" --hidden-import="mss" --hidden-import="pygetwindow" --hidden-import="winrt.windows.media.ocr" --hidden-import="winrt.windows.graphics.imaging" --hidden-import="winrt.windows.storage.streams" translator_app.py

echo.
echo Build complete! You can find the executable in the "dist\RealtimeTranslator" folder.
pause
