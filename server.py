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
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error initializing Google Sheets: {e}")
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
        
        # Headers for each sheet
        requests_data = [
            {
                'range': f"{SHEETS['students']}!A1:H1",
                'values': [['Mã sinh viên', 'Họ tên', 'Môn', 'Nộp bài', 'Quiz', 'Điểm danh', 'Tổng điểm', 'Ghi chú']]
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
        
        for req in requests_data:
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=req['range'],
                valueInputOption='RAW',
                body={'values': req['values']}
            ).execute()
        
        return jsonify({
            'success': True,
            'message': 'Đã khởi tạo sheets thành công!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Sync student
@app.route('/api/sync-student', methods=['POST'])
def sync_student():
    try:
        data = request.json
        student_data = data['studentData']
        stats = data['stats']
        service = get_sheets_service()
        
        # Check if student exists (kiểm tra theo mã sinh viên)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEETS['students']}!A:A"
        ).execute()
        
        values = result.get('values', [])
        student_ids = [row[0] for row in values[1:] if row]  # Bỏ header, lấy cột A (Mã sinh viên)
        
        # Tính tổng điểm: Điểm danh + Quiz
        total_score = stats.get('totalAttendance', 0) + stats.get('averageScore', 0)
        
        row = [[
            student_data['id'],  # Mã sinh viên
            student_data['name'],  # Họ tên
            'Hệ thống kinh doanh thương mại',  # Môn học mặc định
            '',  # Nộp bài - để trống
            stats.get('averageScore', 0),  # Quiz
            stats.get('totalAttendance', 0),  # Điểm danh
            total_score,  # Tổng điểm
            ''  # Ghi chú - để trống
        ]]
        
        if student_data['id'] in student_ids:
            # Update existing (tìm theo mã sinh viên)
            index = student_ids.index(student_data['id']) + 2  # +1 cho header, +1 cho index
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEETS['students']}!A{index}:H{index}",
                valueInputOption='RAW',
                body={'values': row}
            ).execute()
        else:
            # Append new
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEETS['students'],
                valueInputOption='RAW',
                body={'values': row}
            ).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync attendance
@app.route('/api/sync-attendance', methods=['POST'])
def sync_attendance():
    try:
        data = request.json
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
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEETS['attendance'],
            valueInputOption='RAW',
            body={'values': row}
        ).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Sync quiz
@app.route('/api/sync-quiz', methods=['POST'])
def sync_quiz():
    try:
        data = request.json
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
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEETS['quiz'],
            valueInputOption='RAW',
            body={'values': row}
        ).execute()
        
        return jsonify({'success': True})
    except Exception as e:
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
