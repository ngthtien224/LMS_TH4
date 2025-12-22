# 🚀 Hướng Dẫn Chạy Hệ Thống

## 📋 Yêu cầu hệ thống

Bạn cần cài đặt **Node.js** để chạy backend server.

### Cách 1: Sử dụng Node.js (Khuyến nghị)

#### Bước 1: Cài đặt Node.js

1. Truy cập: https://nodejs.org/
2. Download **LTS version** (ví dụ: v20.x.x)
3. Chạy file cài đặt và làm theo hướng dẫn
4. Khởi động lại PowerShell/Command Prompt

#### Bước 2: Kiểm tra cài đặt

```powershell
node --version
npm --version
```

Nếu hiển thị số version là thành công!

#### Bước 3: Cài đặt dependencies

```powershell
cd "d:\M. he-thong-kinh-doanh-tm\Thực hành\TH4"
npm install
```

#### Bước 4: Chạy server

```powershell
npm start
```

hoặc

```powershell
node server.js
```

#### Bước 5: Mở ứng dụng

Mở trình duyệt và truy cập: **http://localhost:3000**

---

### Cách 2: Sử dụng Python (Đơn giản hơn)

Nếu bạn đã có Python, tôi đã tạo sẵn file `server.py`.

#### Bước 1: Kiểm tra Python

```powershell
python --version
```

#### Bước 2: Cài đặt thư viện

```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client flask flask-cors
```

#### Bước 3: Chạy server Python

```powershell
python server.py
```

#### Bước 4: Mở ứng dụng

Mở trình duyệt và truy cập: **http://localhost:3000**

---

## ✅ Kiểm tra hoạt động

1. Sau khi server chạy, mở trình duyệt
2. Vào **http://localhost:3000**
3. Đăng nhập với thông tin học viên
4. Nhấn nút **☁️ Google Sheets**
5. Nhấn **🔌 Kiểm tra kết nối**
6. Nếu thành công, nhấn **🔄 Đồng bộ toàn bộ dữ liệu**

---

## 🔧 Xử lý lỗi

### Lỗi: "Cannot find module 'express'"
**Giải pháp**: Chạy `npm install` trong thư mục dự án

### Lỗi: "EADDRINUSE: address already in use :::3000"
**Giải pháp**: Cổng 3000 đã được sử dụng
- Đóng các ứng dụng đang dùng cổng 3000
- Hoặc thay đổi PORT trong file server.js

### Lỗi: "Permission denied" với credentials.json
**Giải pháp**: 
1. Kiểm tra file credentials.json có trong thư mục
2. Kiểm tra quyền truy cập file

---

## 📊 Cấu trúc Google Sheets

Server sẽ tự động tạo 3 sheets:

1. **Danh sách học sinh** - Thông tin và thống kê
2. **Điểm danh** - Lịch sử điểm danh
3. **Kết quả Quiz** - Điểm số quiz

Spreadsheet ID đang sử dụng: `1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA`

---

## 🔒 Bảo mật

- File **credentials.json** chứa private key
- **KHÔNG** commit file này lên Git
- **KHÔNG** chia sẻ file này với người khác
- Service account đã được cấu hình sẵn quyền truy cập

---

## 📝 Tính năng tự động đồng bộ

✅ Tự động đồng bộ sau mỗi lần điểm danh
✅ Tự động đồng bộ sau mỗi lần làm quiz
✅ Cập nhật thống kê realtime trên Google Sheets

---

Chúc bạn sử dụng thành công! 🎉
