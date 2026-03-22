# Real-time Translator

Ứng dụng dịch thuật trực tiếp (Real-time Translator) trên màn hình máy tính dành cho Windows. Ứng dụng này cho phép bạn chọn một cửa sổ đang mở bất kỳ, nhận diện văn bản (OCR) trên cửa sổ đó và dịch sang ngôn ngữ mục tiêu ngay trên màn hình theo thời gian thực.

## 🌟 Tính năng
- Quét và nhận diện chữ (OCR) trực tiếp từ trên cửa sổ ứng dụng (Sử dụng Windows Native OCR rất nhẹ và nhanh).
- Dịch văn bản theo thời gian thực (Real-time) và hiển thị đè (overlay) lên đúng vị trí trên cửa sổ.
- Xử lý dịch thuật hoàn toàn tại máy tính cá nhân (Local) thông qua **Ollama**, đảm bảo tính riêng tư và không tốn phí API.
- Hỗ trợ nhiều ngôn ngữ đích (Việt Nam, Anh, Tây Ban Nha, Pháp, Nhật, Hàn, Trung, Đức, Ý,...).

## 🚀 Yêu cầu hệ thống và Cài đặt

### 1. Cài đặt Python và Môi trường
- Yêu cầu Python 3.8 trở lên (hoạt động tốt nhất trên Windows 10/11 do sử dụng Windows Native OCR).
- Cài đặt các thư viện cần thiết bằng cách chạy file `start.bat` (file này sẽ tự động cài `requirements.txt`).

### 2. Cài đặt Ollama và Model AI (BẮT BUỘC)
Ứng dụng sử dụng mô hình ngôn ngữ lớn (LLM) cục bộ qua **Ollama** để dịch thuật. Bạn cần cài đặt Ollama và tải model AI về máy.

* **Bước 1**: Tải và cài đặt Ollama tại: [https://ollama.com/](https://ollama.com/)
* **Bước 2**: Mở Command Prompt (cmd) hoặc Terminal và chạy lệnh sau để tải model AI mặc định của ứng dụng là **`qwen2:1.5b`** (dung lượng nhẹ, tốc độ phản hồi nhanh, phù hợp cá nhân):
  ```bash
  ollama run qwen2:1.5b
  ```
  *(Lưu ý: Bạn phải giữ cho Ollama luôn chạy ngầm trong khay hệ thống khi sử dụng ứng dụng).*

*(Nếu bạn muốn sử dụng model AI khác mạnh hơn như `llama3` hoặc `qwen2.5`, bạn hãy mở file `translator_app.py`, tìm đến dòng 30 (`self.model_name = "qwen2:1.5b"`) và sửa thành tên model mới).*

## 💡 Hướng dẫn sử dụng

1. Mở file **`start.bat`** (Click đúp chuột). Script này sẽ tự động kiểm tra môi trường và khởi động ứng dụng.
2. Tại bảng điều khiển chính (Window Translator Control):
   - **Select Window to Translate**: Chọn cửa sổ ứng dụng/game mà bạn muốn dịch. Nếu không thấy cửa sổ cần tìm, hãy bấm nút **Refresh Windows**.
   - **Target Language**: Chọn ngôn ngữ bạn muốn dịch sang (mặc định là tiếng Việt - Vietnamese).
3. Bấm nút **Start Translating** màu xanh để bắt đầu.
   - Ứng dụng sẽ tự động tạo một lớp phủ trong suốt bám theo cửa sổ bạn đã chọn.
   - Máy quét OCR sẽ liên tục đọc và dịch chữ gốc tại cửa sổ đó. Khi có kết quả, chữ dịch sẽ hiển thị (màu vàng trên nền đen) đè đúng lên vị trí của dòng chữ gốc.
4. Để kết thúc, quay lại bảng điều khiển và bấm **Stop**, hoặc tắt hẳn ứng dụng.
