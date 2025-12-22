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
    'attendance': 'Điểm danh',
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
                'values': [['Họ tên', 'Môn', 'Nộp bài', 'Quiz', 'Điểm danh', 'Tổng điểm', 'Ghi chú']]
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

# Sync student
@app.route('/api/sync-student', methods=['POST'])
def sync_student():
    try:
        data = request.json
        print(f"👤 Nhận request sync student: {data}")
        
        student_data = data['studentData']
        stats = data['stats']
        service = get_sheets_service()
        
        # Check if student exists (kiểm tra theo tên)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['students']}!A:A"
        ).execute()
        
        values = result.get('values', [])
        student_names = [row[0] for row in values[1:] if row]  # Bỏ header, lấy cột A (Họ tên)
        
        print(f"📋 Danh sách học sinh hiện có: {student_names}")
        
        # Lấy điểm số từ stats
        quiz_score = stats.get('averageScore', 0)  # Điểm quiz trung bình
        attendance_count = stats.get('totalAttendance', 0)  # Số lần điểm danh
        
        # Tính tổng điểm: Điểm quiz + Số lần điểm danh
        total_score = quiz_score + attendance_count
        
        row = [[
            student_data['name'],  # A: Họ tên
            'Hệ thống kinh doanh thương mại',  # B: Môn
            '',  # C: Nộp bài - để trống
            quiz_score,  # D: Quiz (điểm trung bình)
            attendance_count,  # E: Điểm danh (số lần)
            total_score,  # F: Tổng điểm
            ''  # G: Ghi chú - để trống
        ]]
        
        print(f"📝 Dữ liệu chuẩn bị ghi: {row}")
        
        if student_data['name'] in student_names:
            # Update existing (tìm theo tên)
            index = student_names.index(student_data['name']) + 2  # +1 cho header, +1 cho index
            print(f"🔄 Cập nhật học sinh tại dòng {index}")
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['students']}!A{index}:G{index}",
                valueInputOption='RAW',
                body={'values': row}
            ).execute()
            print(f"✅ Cập nhật thành công: {result.get('updatedCells')} cells")
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
    except Exception as e:
        print(f"❌ Lỗi sync student: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync attendance
@app.route('/api/sync-attendance', methods=['POST'])
def sync_attendance():
    try:
        data = request.json
        print(f"📋 Nhận request sync attendance: {data}")
        
        attendance = data['attendanceRecord']
        student = data['studentData']
        service = get_sheets_service()
        
        # Format date from YYYY-MM-DD to DD/MM/YYYY
        date_parts = attendance['date'].split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        
        row = [[
            student['id'],
            student['name'],
            formatted_date,
            attendance['time'],
            'Có mặt'
        ]]
        
        print(f"📝 Ghi vào sheet: {row}")
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEETS['attendance'],
            valueInputOption='RAW',
            body={'values': row}
        ).execute()
        
        print(f"✅ Đồng bộ điểm danh thành công: {result.get('updates')}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Lỗi sync attendance: {str(e)}")
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
