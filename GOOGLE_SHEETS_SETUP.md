# 📘 Hướng Dẫn Cấu Hình Google Sheets API

Hướng dẫn này sẽ giúp bạn thiết lập kết nối Google Sheets để lưu trữ dữ liệu điểm danh và quiz của học sinh.

## 📋 Mục Lục
1. [Tạo Google Sheets](#1-tạo-google-sheets)
2. [Lấy API Key](#2-lấy-api-key)
3. [Cấu hình trong ứng dụng](#3-cấu-hình-trong-ứng-dụng)
4. [Cấu trúc dữ liệu](#4-cấu-trúc-dữ-liệu)
5. [Xử lý lỗi thường gặp](#5-xử-lý-lỗi-thường-gặp)

---

## 1. Tạo Google Sheets

### Bước 1.1: Tạo Sheet mới
1. Truy cập [Google Sheets](https://sheets.google.com)
2. Nhấn **+ Blank** để tạo spreadsheet mới
3. Đặt tên: **"Hệ Thống Học Tập"**

### Bước 1.2: Tạo 3 sheet con
Tạo 3 sheet với tên chính xác như sau (phân biệt hoa thường):

1. **Danh sách học sinh**
2. **Điểm danh**
3. **Kết quả Quiz**

**Cách tạo sheet con:**
- Nhấn nút **+** ở góc dưới bên trái
- Nhấp đúp vào tên sheet để đổi tên

### Bước 1.3: Lấy Spreadsheet ID
1. Mở Google Sheet vừa tạo
2. Xem URL trên thanh địa chỉ:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123xyz456DEF/edit
   ```
3. Copy phần giữa `/d/` và `/edit`:
   - **Spreadsheet ID**: `1ABC123xyz456DEF`
4. Lưu ID này để sử dụng sau

---

## 2. Lấy API Key

### Bước 2.1: Vào Google Cloud Console
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Đăng nhập bằng tài khoản Google của bạn

### Bước 2.2: Tạo Project mới
1. Nhấn vào dropdown **Select a project** ở thanh trên
2. Chọn **NEW PROJECT**
3. Đặt tên project: **"Learning System"**
4. Nhấn **CREATE**

### Bước 2.3: Kích hoạt Google Sheets API
1. Trong menu bên trái, chọn **APIs & Services** → **Library**
2. Tìm kiếm: **"Google Sheets API"**
3. Nhấn vào **Google Sheets API**
4. Nhấn nút **ENABLE**

### Bước 2.4: Tạo API Key
1. Trong menu bên trái, chọn **APIs & Services** → **Credentials**
2. Nhấn **+ CREATE CREDENTIALS** ở trên
3. Chọn **API key**
4. API key sẽ được tạo tự động
5. **Copy API key** này (dạng: `AIzaSyD-abc123xyz456...`)
6. (Tùy chọn) Nhấn **RESTRICT KEY** để bảo mật:
   - **API restrictions**: Chọn **Restrict key**
   - Chỉ chọn: **Google Sheets API**
   - Nhấn **SAVE**

---

## 3. Cấu hình trong ứng dụng

### Bước 3.1: Chia sẻ Google Sheet
**QUAN TRỌNG**: Phải chia sẻ sheet với chế độ public để API có thể truy cập

1. Mở Google Sheet của bạn
2. Nhấn nút **Share** (góc trên bên phải)
3. Chọn **Change to anyone with the link**
4. Đặt quyền: **Viewer** (Chỉ xem)
   - ⚠️ **Lưu ý**: Vì dùng API Key, sheet phải ở chế độ public. Để bảo mật hơn, nên dùng OAuth 2.0 (nâng cao)
5. Nhấn **Done**

### Bước 3.2: Nhập thông tin vào ứng dụng
1. Mở file `index.html` trong trình duyệt
2. Đăng nhập vào hệ thống
3. Nhấn nút **☁️ Google Sheets** ở footer
4. Điền thông tin:
   - **Google Sheets API Key**: Paste API key đã copy
   - **Spreadsheet ID**: Paste Spreadsheet ID đã copy
5. Nhấn **🔌 Kiểm tra kết nối** để test
6. Nếu thành công, nhấn **💾 Lưu cấu hình**

### Bước 3.3: Đồng bộ dữ liệu
1. Sau khi lưu cấu hình, phần đồng bộ sẽ hiện ra
2. Nhấn **🔄 Đồng bộ toàn bộ dữ liệu**
3. Hệ thống sẽ tự động:
   - Tạo header cho 3 sheets
   - Upload toàn bộ dữ liệu điểm danh
   - Upload toàn bộ dữ liệu quiz
   - Cập nhật thông tin học sinh

---

## 4. Cấu trúc dữ liệu

### Sheet: "Danh sách học sinh"
| Cột | Tên | Mô tả |
|-----|-----|-------|
| A | Mã học viên | ID sinh viên |
| B | Họ tên | Tên đầy đủ |
| C | Ngày đăng ký | Ngày đăng ký hệ thống |
| D | Tổng điểm danh | Số lần điểm danh |
| E | Tổng quiz | Số quiz đã làm |
| F | Điểm TB | Điểm trung bình các quiz |
| G | Điểm cao nhất | Điểm cao nhất đạt được |

### Sheet: "Điểm danh"
| Cột | Tên | Mô tả |
|-----|-----|-------|
| A | Mã học viên | ID sinh viên |
| B | Họ tên | Tên đầy đủ |
| C | Ngày | Ngày điểm danh |
| D | Giờ | Giờ điểm danh |
| E | Trạng thái | "Có mặt" |

### Sheet: "Kết quả Quiz"
| Cột | Tên | Mô tả |
|-----|-----|-------|
| A | Mã học viên | ID sinh viên |
| B | Họ tên | Tên đầy đủ |
| C | Ngày | Ngày làm quiz |
| D | Điểm | Điểm số (0-100) |
| E | Số câu đúng | Số câu trả lời đúng |
| F | Tổng câu hỏi | Tổng số câu hỏi |
| G | Phần trăm | % câu đúng |

---

## 5. Xử lý lỗi thường gặp

### ❌ Lỗi: "API key not valid"
**Nguyên nhân**: API Key sai hoặc chưa kích hoạt

**Giải pháp**:
- Kiểm tra lại API Key có chính xác không
- Đảm bảo đã Enable Google Sheets API
- Đợi vài phút sau khi tạo API key

### ❌ Lỗi: "The caller does not have permission"
**Nguyên nhân**: Google Sheet chưa được chia sẻ public

**Giải pháp**:
1. Mở Google Sheet
2. Nhấn **Share**
3. Chọn **Anyone with the link** → **Viewer**
4. Thử lại

### ❌ Lỗi: "Requested entity was not found"
**Nguyên nhân**: Spreadsheet ID sai hoặc sheet con sai tên

**Giải pháp**:
- Kiểm tra lại Spreadsheet ID
- Đảm bảo có 3 sheets với tên chính xác:
  - `Danh sách học sinh`
  - `Điểm danh`
  - `Kết quả Quiz`

### ❌ Lỗi: "The request is missing a valid API key"
**Nguyên nhân**: Chưa nhập API Key

**Giải pháp**:
- Vào phần Google Sheets trong app
- Nhập đầy đủ API Key và Spreadsheet ID

---

## 🎯 Tính năng tự động

Sau khi cấu hình thành công, hệ thống sẽ **TỰ ĐỘNG** đồng bộ:

✅ **Sau mỗi lần điểm danh**
- Thêm dòng mới vào sheet "Điểm danh"
- Cập nhật thống kê trong "Danh sách học sinh"

✅ **Sau mỗi lần làm quiz**
- Thêm dòng mới vào sheet "Kết quả Quiz"
- Cập nhật điểm trung bình và điểm cao nhất

---

## 🔒 Bảo mật

### Khuyến nghị:
1. **Không public API Key**: Không share file HTML chứa API key
2. **Chỉ chia sẻ View**: Đặt quyền sheet là "Viewer" chứ không phải "Editor"
3. **Restrict API Key**: 
   - Giới hạn chỉ dùng cho Google Sheets API
   - Có thể thêm HTTP referrer restrictions
4. **Backup định kỳ**: Sao lưu Google Sheet thường xuyên

### Nâng cao (cho chuyên gia):
Để bảo mật tốt hơn, có thể sử dụng:
- **OAuth 2.0** thay vì API Key (phức tạp hơn nhưng an toàn hơn)
- **Google Apps Script** làm backend trung gian
- **Service Account** cho ứng dụng server-side

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra lại từng bước trong hướng dẫn
2. Xem phần "Xử lý lỗi thường gặp"
3. Nhấn F12 trong trình duyệt → tab Console để xem lỗi chi tiết

---

## ✅ Checklist tổng hợp

- [ ] Đã tạo Google Sheet với 3 sheet con đúng tên
- [ ] Đã lấy được Spreadsheet ID
- [ ] Đã tạo project trên Google Cloud Console
- [ ] Đã Enable Google Sheets API
- [ ] Đã tạo API Key
- [ ] Đã chia sẻ Google Sheet với chế độ "Anyone with the link - Viewer"
- [ ] Đã nhập API Key và Spreadsheet ID vào app
- [ ] Đã test kết nối thành công
- [ ] Đã đồng bộ toàn bộ dữ liệu lần đầu

---

**Chúc bạn sử dụng thành công! 🎉**
