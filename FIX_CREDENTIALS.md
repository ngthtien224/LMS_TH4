# 🔧 Hướng dẫn tạo lại Service Account Credentials

## Vấn đề: "Invalid JWT Signature"

Lỗi này xảy ra vì:
- Credentials bị vô hiệu hóa hoặc hết hạn
- Service account không có quyền truy cập Sheet
- Credentials bị lỗi

## ✅ Giải pháp: Tạo lại credentials mới

### Bước 1: Vào Google Cloud Console

1. Truy cập: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google của bạn
3. Chọn project: **marketstack-sheets-480804**

### Bước 2: Tạo Service Account mới

1. Từ menu bên trái, chọn: **IAM & Admin** → **Service Accounts**
2. Click **CREATE SERVICE ACCOUNT**
3. Điền thông tin:
   - **Service account name**: `lms-sheets-service`
   - **Service account ID**: tự động tạo
   - **Description**: `Service account for LMS Google Sheets integration`
4. Click **CREATE AND CONTINUE**
5. **Grant this service account access to project**:
   - Role: **Editor** (hoặc **Basic** → **Editor**)
6. Click **CONTINUE** → **DONE**

### Bước 3: Tạo Key (Credentials)

1. Trong danh sách Service Accounts, tìm service account vừa tạo
2. Click vào tên service account
3. Chuyển sang tab **KEYS**
4. Click **ADD KEY** → **Create new key**
5. Chọn format: **JSON**
6. Click **CREATE**
7. File JSON sẽ được download về máy tính của bạn

### Bước 4: Thay thế credentials.json

1. Rename file JSON vừa download thành: `credentials.json`
2. Copy file này vào thư mục project: `d:\M. he-thong-kinh-doanh-tm\LMS_TH4\`
3. Thay thế file cũ

### Bước 5: Lấy Service Account Email

1. Mở file `credentials.json` vừa tạo
2. Tìm dòng `"client_email"`, copy email đó
3. Ví dụ: `lms-sheets-service@marketstack-sheets-480804.iam.gserviceaccount.com`

### Bước 6: Share Google Sheet

1. Mở Google Sheet của bạn:
   https://docs.google.com/spreadsheets/d/1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA/edit

2. Click nút **"Share"** (Chia sẻ) ở góc phải trên

3. Paste service account email vừa copy vào

4. Chọn quyền: **Editor** (Có thể chỉnh sửa)

5. **Bỏ tick** "Notify people"

6. Click **Send**

### Bước 7: Test kết nối

```bash
python test_sheets.py
```

Nếu thấy "✅ KẾT NỐI THÀNH CÔNG!" là OK!

### Bước 8: Deploy lên Render

Khi deploy lên Render, bạn cần thêm credentials:

1. Vào **Render Dashboard** → Your Service → **Environment**

2. Add **Secret File**:
   - Filename: `credentials.json`
   - Contents: Copy toàn bộ nội dung file credentials.json

3. Hoặc dùng Environment Variable:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: Copy toàn bộ nội dung file credentials.json (dạng JSON string)

## 📝 Lưu ý quan trọng:

- ⚠️ KHÔNG commit file credentials.json lên GitHub (đã có trong .gitignore)
- ⚠️ Giữ credentials an toàn, đây là thông tin nhạy cảm
- ✅ Mỗi khi deploy lên Render, phải add credentials vào Secret Files

## 🆘 Nếu vẫn lỗi:

Liên hệ với tôi và cung cấp:
1. Screenshot màn hình lỗi
2. Log trong Console (F12)
3. Log trong terminal khi chạy server
