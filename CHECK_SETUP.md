# Hướng dẫn Fix Lỗi "Invalid JWT Signature"

## Nguyên nhân:
Lỗi này xảy ra khi Google không thể xác thực service account credentials.

## Các bước kiểm tra và sửa:

### Bước 1: Kiểm tra Service Account có quyền truy cập Sheet chưa

1. Mở Google Sheet của bạn: https://docs.google.com/spreadsheets/d/1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA/edit

2. Click nút **"Share"** (Chia sẻ) ở góc phải trên

3. Thêm email service account vào:
   ```
   sheets-updater-service@marketstack-sheets-480804.iam.gserviceaccount.com
   ```

4. Chọn quyền: **Editor** (Có thể chỉnh sửa)

5. Bỏ tick "Notify people" (không cần thông báo)

6. Click **Send**

### Bước 2: Kiểm tra file credentials.json trên Render

Khi deploy lên Render, bạn cần thêm credentials như một **Environment Variable** hoặc **Secret File**.

**Cách 1: Sử dụng Environment Variable**

1. Vào Render Dashboard → Your Service → Environment

2. Thêm biến môi trường:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: Copy toàn bộ nội dung file credentials.json (dạng JSON string)

3. Sửa code server.py để đọc từ environment variable

**Cách 2: Upload Secret File (Khuyên dùng)**

1. Vào Render Dashboard → Your Service → Settings

2. Scroll xuống "Secret Files"

3. Add Secret File:
   - Filename: `credentials.json`
   - Contents: Copy toàn bộ nội dung file credentials.json

### Bước 3: Kiểm tra thời gian hệ thống

Chạy lệnh kiểm tra:
```bash
python -c "import datetime; print(datetime.datetime.now())"
```

Nếu thời gian không đúng, JWT signature sẽ không hợp lệ.

### Bước 4: Test lại

1. Chạy server local:
   ```bash
   python server.py
   ```

2. Mở browser: http://localhost:3000

3. Thử điểm danh hoặc làm quiz

4. Kiểm tra Console (F12) xem còn lỗi không

## Nếu vẫn còn lỗi:

Tạo lại Service Account mới:

1. Vào [Google Cloud Console](https://console.cloud.google.com/)

2. Chọn project: **marketstack-sheets-480804**

3. IAM & Admin → Service Accounts

4. Tạo service account mới

5. Tạo key mới (JSON format)

6. Download và thay thế file credentials.json cũ

7. Nhớ chia sẻ Google Sheet cho service account mới!
