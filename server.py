from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Sheet names
SHEETS = {
    'students': 'Danh sách học sinh',
    'attendance': 'Diemdanh',
    'quiz': 'Kết quả Quiz'
}

# Initialize Google Sheets API
def get_sheets_service():
    try:
        # Thử đọc từ environment variable trước (cho Render/Production)
        google_creds = os.environ.get('GOOGLE_KEY')
        
        if google_creds:
            # Nếu có env variable, parse JSON string
            creds_dict = json.loads(google_creds)
            
            # FIX: Sửa lỗi xuống dòng trong private_key (quan trọng!)
            # Khi copy vào Render, \n bị hiểu thành \\n, cần chuyển lại
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
            
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            print("🔑 Đã tải credentials từ biến môi trường GOOGLE_KEY")
        else:
            # Nếu không có env variable, đọc từ file (cho Local)
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Không tìm thấy file {CREDENTIALS_FILE}")
            credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES)
            print(f"✅ Đã tải credentials từ file {CREDENTIALS_FILE}")
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"❌ Error initializing Google Sheets: {e}")
        raise

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Test connection
@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    try:
        service = get_sheets_service()
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()
        
        return jsonify({
            'success': True,
            'message': 'Kết nối thành công!',
            'sheetTitle': spreadsheet.get('properties', {}).get('title', 'Unknown')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Initialize sheets
@app.route('/api/initialize-sheets', methods=['POST'])
def initialize_sheets():
    try:
        service = get_sheets_service()
        
        print("🔧 Đang khởi tạo headers cho các sheet...")
        
        # Headers for each sheet
        requests_data = [
            {
                'range': f"{SHEETS['students']}!A1:G1",
                'values': [['Mã học viên', 'Họ tên', 'Ngày đăng ký', 'Tổng điểm danh', 'Tổng quiz', 'Điểm TB', 'Điểm cao nhất']]
            },
            {
                'range': f"{SHEETS['attendance']}!A1:E1",
                'values': [['Mã học viên', 'Họ tên', 'Ngày', 'Giờ', 'Trạng thái']]
            },
            {
                'range': f"{SHEETS['quiz']}!A1:G1",
                'values': [['Mã học viên', 'Họ tên', 'Ngày', 'Điểm', 'Số câu đúng', 'Tổng câu hỏi', 'Phần trăm']]
            }
        ]
        
        # Cập nhật headers
        for req in requests_data:
            print(f"📝 Tạo header cho {req['range']}: {req['values']}")
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=req['range'],
                valueInputOption='RAW',
                body={'values': req['values']}
            ).execute()
            print(f"✅ Đã tạo header: {result.get('updatedCells')} cells")
        
        # Format headers (in đậm, nền màu)
        batch_update_request = {
            'requests': [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,  # Sheet đầu tiên
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 7
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                                'textFormat': {
                                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                    'fontSize': 11,
                                    'bold': True
                                },
                                'horizontalAlignment': 'CENTER'
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                    }
                }
            ]
        }
        
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=batch_update_request
            ).execute()
            print("🎨 Đã format header")
        except Exception as format_error:
            print(f"⚠️ Không thể format header: {format_error}")
        
        return jsonify({
            'success': True,
            'message': 'Đã khởi tạo sheets thành công với headers đầy đủ!'
        })
    except Exception as e:
        print(f"❌ Lỗi khởi tạo sheets: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Sync student - ĐÃ TẮT
@app.route('/api/sync-student', methods=['POST'])
def sync_student():
    try:
        # COMMENT: Tạm tắt việc lưu vào sheet Danh sách học sinh
        print("⚠️ Sync student đã bị tắt")
        return jsonify({'success': True, 'message': 'Sync student đã bị tắt'})
        
        """
        data = request.json
        print(f"👤 Nhận request sync student: {data}")
        
        student_data = data['studentData']
        stats = data['stats']
        service = get_sheets_service()
        
        # Check if sheet has header (kiểm tra xem dòng đầu có phải header không)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['students']}!A1:G1"
        ).execute()
        
        first_row = result.get('values', [])
        
        # Nếu chưa có header hoặc header sai, tạo mới
        if not first_row or first_row[0][0] != 'Mã học viên':
            print("🔧 Chưa có header, đang tạo header...")
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['students']}!A1:G1",
                valueInputOption='RAW',
                body={'values': [['Mã học viên', 'Họ tên', 'Ngày đăng ký', 'Tổng điểm danh', 'Tổng quiz', 'Điểm TB', 'Điểm cao nhất']]}
            ).execute()
            print("✅ Đã tạo header")
        
        # Check if student exists (kiểm tra theo mã học viên)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['students']}!A:A"
        ).execute()
        
        values = result.get('values', [])
        student_ids = [row[0] for row in values[1:] if row]  # Bỏ header, lấy cột A (Mã học viên)
        
        print(f"📋 Danh sách mã học viên hiện có: {student_ids}")
        
        # Lấy dữ liệu từ stats
        total_attendance = stats.get('totalAttendance', 0)  # Tổng số lần điểm danh
        total_quizzes = stats.get('totalQuizzes', 0)  # Tổng số quiz đã làm
        average_score = stats.get('averageScore', 0)  # Điểm trung bình
        highest_score = stats.get('highestScore', 0)  # Điểm cao nhất
        
        # Format ngày đăng ký (lấy từ studentData hoặc dùng ngày hiện tại)
        from datetime import datetime
        if 'registeredDate' in student_data:
            reg_date = student_data['registeredDate'][:10]  # YYYY-MM-DD
            date_parts = reg_date.split('-')
            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"  # DD/MM/YYYY
        else:
            formatted_date = datetime.now().strftime('%d/%m/%Y')
        
        row = [[
            student_data['id'],  # A: Mã học viên
            student_data['name'],  # B: Họ tên
            formatted_date,  # C: Ngày đăng ký
            total_attendance,  # D: Tổng điểm danh
            total_quizzes,  # E: Tổng quiz
            average_score,  # F: Điểm TB
            highest_score  # G: Điểm cao nhất
        ]]
        
        print(f"📝 Dữ liệu chuẩn bị ghi: {row}")
        
        if student_data['id'] in student_ids:
            # Update existing (tìm theo mã học viên, KHÔNG tạo dòng mới)
            index = student_ids.index(student_data['id']) + 2  # +1 cho header, +1 cho index
            print(f"🔄 Cập nhật học sinh tại dòng {index}")
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['students']}!A{index}:G{index}",
                valueInputOption='RAW',
                body={'values': row}
            ).execute()
            print(f"✅ Cập nhật thành công: {result.get('updatedCells')} cells")
        else:
            # Append new
            print(f"➕ Thêm học sinh mới: {student_data['name']}")
            result = service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEETS['students'],
                valueInputOption='RAW',
                body={'values': row}
            ).execute()
            print(f"✅ Thêm thành công: {result.get('updates')}")
        
        return jsonify({'success': True})
        """
    except Exception as e:
        print(f"❌ Lỗi sync student: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync attendance
@app.route('/api/sync-attendance', methods=['POST'])
def sync_attendance():
    try:
        data = request.json
        print(f"📋 ===== BẮT ĐẦU SYNC ATTENDANCE =====")
        print(f"📋 Data nhận được: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        attendance = data['attendanceRecord']
        student = data['studentData']
        
        print(f"👤 Student info: ID={student['id']}, Name={student['name']}")
        print(f"📅 Attendance: date={attendance['date']}, time={attendance['time']}")
        
        service = get_sheets_service()
        print(f"✅ Đã kết nối Google Sheets service")
        
        # Check sheet name
        print(f"📊 Sheet name: '{SHEETS['attendance']}'")
        
        # Check if sheet has header
        print(f"🔍 Kiểm tra header tại: {SHEETS['attendance']}!A1:E1")
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['attendance']}!A1:E1"
        ).execute()
        
        first_row = result.get('values', [])
        print(f"📋 First row hiện tại: {first_row}")
        
        # Nếu chưa có header, tạo mới
        if not first_row or (len(first_row[0]) > 0 and first_row[0][0] != 'Mã học viên'):
            print("🔧 Chưa có header hoặc header sai, đang tạo...")
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['attendance']}!A1:E1",
                valueInputOption='RAW',
                body={'values': [['Mã học viên', 'Họ tên', 'Ngày', 'Giờ', 'Trạng thái']]}
            ).execute()
            print("✅ Đã tạo header")
        else:
            print("✅ Header đã tồn tại")
        
        # Format date from YYYY-MM-DD to DD/MM/YYYY
        date_parts = attendance['date'].split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        print(f"📅 Date formatted: {attendance['date']} -> {formatted_date}")
        
        row = [[
            student['id'],
            student['name'],
            formatted_date,
            attendance['time'],
            'Có mặt'
        ]]
        
        print(f"📝 Dữ liệu chuẩn bị ghi: {row}")
        print(f"🎯 Ghi vào range: {SHEETS['attendance']}")
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEETS['attendance'],
            valueInputOption='RAW',
            body={'values': row}
        ).execute()
        
        print(f"✅ ===== ĐỒNG BỘ THÀNH CÔNG =====")
        print(f"✅ Updates: {result.get('updates')}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ ===== LỖI SYNC ATTENDANCE =====")
        print(f"❌ Lỗi: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync quiz
@app.route('/api/sync-quiz', methods=['POST'])
def sync_quiz():
    try:
        data = request.json
        print(f"📝 Nhận request sync quiz: {data}")
        
        quiz = data['quizRecord']
        student = data['studentData']
        service = get_sheets_service()
        
        # Check if sheet has header
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['quiz']}!A1:G1"
        ).execute()
        
        first_row = result.get('values', [])
        
        # Nếu chưa có header, tạo mới
        if not first_row or first_row[0][0] != 'Mã học viên':
            print("🔧 Chưa có header cho Quiz, đang tạo...")
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['quiz']}!A1:G1",
                valueInputOption='RAW',
                body={'values': [['Mã học viên', 'Họ tên', 'Ngày', 'Điểm', 'Số câu đúng', 'Tổng câu hỏi', 'Phần trăm']]}
            ).execute()
            print("✅ Đã tạo header")
        
        percentage = round((quiz['correctAnswers'] / quiz['totalQuestions']) * 100)
        
        # Format date
        date_parts = quiz['date'].split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        
        row = [[
            student['id'],
            student['name'],
            formatted_date,
            quiz['score'],
            quiz['correctAnswers'],
            quiz['totalQuestions'],
            f"{percentage}%"
        ]]
        
        print(f"📝 Ghi vào sheet: {row}")
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEETS['quiz'],
            valueInputOption='RAW',
            body={'values': row}
        ).execute()
        
        print(f"✅ Đồng bộ quiz thành công: {result.get('updates')}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Lỗi sync quiz: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync all data
@app.route('/api/sync-all', methods=['POST'])
def sync_all():
    try:
        data = request.json
        student_data = data['studentData']
        attendance_data = data['attendanceData']
        quiz_data = data['quizData']
        stats = data['stats']
        
        # Initialize
        initialize_sheets()
        
        # Sync student
        sync_student_data = {
            'studentData': student_data,
            'stats': stats
        }
        with app.test_request_context(json=sync_student_data):
            sync_student()
        
        # Sync attendance
        for attendance in attendance_data:
            sync_attendance_data = {
                'attendanceRecord': attendance,
                'studentData': student_data
            }
            with app.test_request_context(json=sync_attendance_data):
                sync_attendance()
        
        # Sync quizzes
        for quiz in quiz_data:
            sync_quiz_data = {
                'quizRecord': quiz,
                'studentData': student_data
            }
            with app.test_request_context(json=sync_quiz_data):
                sync_quiz()
        
        return jsonify({
            'success': True,
            'message': f'Đã đồng bộ thành công: {len(attendance_data)} lần điểm danh và {len(quiz_data)} kết quả quiz'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════╗
║   🎓 Learning System Backend Server (Python)       ║
║                                                    ║
║   Server đang chạy tại: http://localhost:3000     ║
║   Spreadsheet ID: 1TKmu6oRIEqyG2PfY__deAhp_8em... ║
║                                                    ║
║   Endpoints:                                       ║
║   - GET  /api/test-connection                      ║
║   - POST /api/initialize-sheets                    ║
║   - POST /api/sync-student                         ║
║   - POST /api/sync-attendance                      ║
║   - POST /api/sync-quiz                            ║
║   - POST /api/sync-all                             ║
║                                                    ║
║   Mở trình duyệt: http://localhost:3000           ║
╚════════════════════════════════════════════════════╝
    """)
    app.run(host='localhost', port=3000, debug=True)
