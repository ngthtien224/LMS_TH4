"""
Script test đồng bộ dữ liệu lên Google Sheets
Kiểm tra xem dữ liệu có ghi đúng cột không
"""
import requests
import json

API_BASE_URL = 'http://localhost:3000/api'

# Test data
student_data = {
    'id': 'SV001',
    'name': 'Nguyễn Văn A Test',
    'registeredDate': '2025-12-22T10:00:00.000Z'
}

attendance_record = {
    'date': '2025-12-22',
    'time': '10:30:00',
    'timestamp': '2025-12-22T10:30:00.000Z'
}

quiz_record = {
    'date': '2025-12-22',
    'score': 85,
    'correctAnswers': 4,
    'totalQuestions': 5,
    'timestamp': '2025-12-22T10:30:00.000Z'
}

stats = {
    'totalAttendance': 1,
    'totalQuizzes': 1,
    'averageScore': 85,
    'highestScore': 85
}

print("=" * 60)
print("TEST ĐỒNG BỘ DỮ LIỆU LÊN GOOGLE SHEETS")
print("=" * 60)

# Test 1: Initialize sheets
print("\n1️⃣ Test khởi tạo sheets...")
try:
    response = requests.post(f"{API_BASE_URL}/initialize-sheets")
    result = response.json()
    print(f"✅ {result.get('message')}")
except Exception as e:
    print(f"❌ Lỗi: {e}")

# Test 2: Sync student
print("\n2️⃣ Test đồng bộ thông tin học sinh...")
print(f"   Mã học viên: {student_data['id']}")
print(f"   Họ tên: {student_data['name']}")
try:
    response = requests.post(
        f"{API_BASE_URL}/sync-student",
        json={'studentData': student_data, 'stats': stats}
    )
    result = response.json()
    if result.get('success'):
        print(f"✅ Đồng bộ học sinh thành công")
        print(f"   Expected columns: Mã học viên | Họ tên | Ngày đăng ký | Tổng điểm danh | Tổng quiz | Điểm TB | Điểm cao nhất")
        print(f"   Data sent: {student_data['id']} | {student_data['name']} | 22/12/2025 | {stats['totalAttendance']} | {stats['totalQuizzes']} | {stats['averageScore']} | {stats['highestScore']}")
    else:
        print(f"❌ {result.get('message')}")
except Exception as e:
    print(f"❌ Lỗi: {e}")

# Test 3: Sync attendance
print("\n3️⃣ Test đồng bộ điểm danh...")
try:
    response = requests.post(
        f"{API_BASE_URL}/sync-attendance",
        json={'attendanceRecord': attendance_record, 'studentData': student_data}
    )
    result = response.json()
    if result.get('success'):
        print(f"✅ Đồng bộ điểm danh thành công")
        print(f"   Expected columns: Mã học viên | Họ tên | Ngày | Giờ | Trạng thái")
        print(f"   Data sent: {student_data['id']} | {student_data['name']} | 22/12/2025 | {attendance_record['time']} | Có mặt")
    else:
        print(f"❌ {result.get('message')}")
except Exception as e:
    print(f"❌ Lỗi: {e}")

# Test 4: Sync quiz
print("\n4️⃣ Test đồng bộ quiz...")
try:
    response = requests.post(
        f"{API_BASE_URL}/sync-quiz",
        json={'quizRecord': quiz_record, 'studentData': student_data}
    )
    result = response.json()
    if result.get('success'):
        print(f"✅ Đồng bộ quiz thành công")
        print(f"   Expected columns: Mã học viên | Họ tên | Ngày | Điểm | Số câu đúng | Tổng câu hỏi | Phần trăm")
        print(f"   Data sent: {student_data['id']} | {student_data['name']} | 22/12/2025 | {quiz_record['score']} | {quiz_record['correctAnswers']} | {quiz_record['totalQuestions']} | 80%")
    else:
        print(f"❌ {result.get('message')}")
except Exception as e:
    print(f"❌ Lỗi: {e}")

print("\n" + "=" * 60)
print("KIỂM TRA GOOGLE SHEETS ĐỂ XEM DỮ LIỆU CÓ ĐÚNG CỘT KHÔNG!")
print("=" * 60)
print("\n📊 Mở link: https://docs.google.com/spreadsheets/d/1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA/edit")
