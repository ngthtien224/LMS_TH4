const express = require('express');
const cors = require('cors');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Load credentials
const CREDENTIALS_PATH = path.join(__dirname, 'credentials.json');
const SPREADSHEET_ID = '1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA';

// Sheet names
const SHEETS = {
    students: 'Danh sách học sinh',
    attendance: 'Điểm danh',
    quiz: 'Kết quả Quiz'
};

// Initialize Google Sheets API
async function getGoogleSheetsClient() {
    try {
        const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
        
        const auth = new google.auth.GoogleAuth({
            credentials: credentials,
            scopes: ['https://www.googleapis.com/auth/spreadsheets'],
        });

        const authClient = await auth.getClient();
        const sheets = google.sheets({ version: 'v4', auth: authClient });
        
        return sheets;
    } catch (error) {
        console.error('Error initializing Google Sheets client:', error);
        throw error;
    }
}

// Test connection endpoint
app.get('/api/test-connection', async (req, res) => {
    try {
        const sheets = await getGoogleSheetsClient();
        const response = await sheets.spreadsheets.get({
            spreadsheetId: SPREADSHEET_ID,
        });
        
        res.json({
            success: true,
            message: 'Kết nối thành công!',
            sheetTitle: response.data.properties.title
        });
    } catch (error) {
        console.error('Connection test failed:', error);
        res.status(500).json({
            success: false,
            message: 'Lỗi kết nối: ' + error.message
        });
    }
});

// Initialize sheets with headers
app.post('/api/initialize-sheets', async (req, res) => {
    try {
        const sheets = await getGoogleSheetsClient();
        
        // Headers for each sheet
        const requests = [
            {
                range: `${SHEETS.students}!A1:G1`,
                values: [['Mã học viên', 'Họ tên', 'Ngày đăng ký', 'Tổng điểm danh', 'Tổng quiz', 'Điểm TB', 'Điểm cao nhất']]
            },
            {
                range: `${SHEETS.attendance}!A1:E1`,
                values: [['Mã học viên', 'Họ tên', 'Ngày', 'Giờ', 'Trạng thái']]
            },
            {
                range: `${SHEETS.quiz}!A1:G1`,
                values: [['Mã học viên', 'Họ tên', 'Ngày', 'Điểm', 'Số câu đúng', 'Tổng câu hỏi', 'Phần trăm']]
            }
        ];

        for (const request of requests) {
            await sheets.spreadsheets.values.update({
                spreadsheetId: SPREADSHEET_ID,
                range: request.range,
                valueInputOption: 'RAW',
                resource: { values: request.values }
            });
        }

        res.json({
            success: true,
            message: 'Đã khởi tạo sheets thành công!'
        });
    } catch (error) {
        console.error('Initialize sheets failed:', error);
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// Sync student data
app.post('/api/sync-student', async (req, res) => {
    try {
        const { studentData, stats } = req.body;
        const sheets = await getGoogleSheetsClient();

        // Check if student exists
        const existingData = await sheets.spreadsheets.values.get({
            spreadsheetId: SPREADSHEET_ID,
            range: `${SHEETS.students}!A:A`
        });

        const studentIds = existingData.data.values ? existingData.data.values.map(row => row[0]) : [];
        const studentIndex = studentIds.indexOf(studentData.id);

        const row = [[
            studentData.id,
            studentData.name,
            new Date(studentData.registeredDate).toLocaleDateString('vi-VN'),
            stats.totalAttendance || 0,
            stats.totalQuizzes || 0,
            stats.averageScore || 0,
            stats.highestScore || 0
        ]];

        if (studentIndex > 0) {
            // Update existing row
            await sheets.spreadsheets.values.update({
                spreadsheetId: SPREADSHEET_ID,
                range: `${SHEETS.students}!A${studentIndex + 1}:G${studentIndex + 1}`,
                valueInputOption: 'RAW',
                resource: { values: row }
            });
        } else {
            // Append new row
            await sheets.spreadsheets.values.append({
                spreadsheetId: SPREADSHEET_ID,
                range: SHEETS.students,
                valueInputOption: 'RAW',
                resource: { values: row }
            });
        }

        res.json({ success: true });
    } catch (error) {
        console.error('Sync student failed:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// Sync attendance
app.post('/api/sync-attendance', async (req, res) => {
    try {
        const { attendanceRecord, studentData } = req.body;
        const sheets = await getGoogleSheetsClient();

        const row = [[
            studentData.id,
            studentData.name,
            attendanceRecord.date.split('-').reverse().join('/'),
            attendanceRecord.time,
            'Có mặt'
        ]];

        await sheets.spreadsheets.values.append({
            spreadsheetId: SPREADSHEET_ID,
            range: SHEETS.attendance,
            valueInputOption: 'RAW',
            resource: { values: row }
        });

        res.json({ success: true });
    } catch (error) {
        console.error('Sync attendance failed:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// Sync quiz
app.post('/api/sync-quiz', async (req, res) => {
    try {
        const { quizRecord, studentData } = req.body;
        const sheets = await getGoogleSheetsClient();

        const percentage = Math.round((quizRecord.correctAnswers / quizRecord.totalQuestions) * 100);
        
        const row = [[
            studentData.id,
            studentData.name,
            quizRecord.date.split('-').reverse().join('/'),
            quizRecord.score,
            quizRecord.correctAnswers,
            quizRecord.totalQuestions,
            `${percentage}%`
        ]];

        await sheets.spreadsheets.values.append({
            spreadsheetId: SPREADSHEET_ID,
            range: SHEETS.quiz,
            valueInputOption: 'RAW',
            resource: { values: row }
        });

        res.json({ success: true });
    } catch (error) {
        console.error('Sync quiz failed:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// Sync all data
app.post('/api/sync-all', async (req, res) => {
    try {
        const { studentData, attendanceData, quizData, stats } = req.body;
        const sheets = await getGoogleSheetsClient();

        // Initialize sheets first
        await fetch(`http://localhost:${PORT}/api/initialize-sheets`, {
            method: 'POST'
        });

        // Sync student
        await fetch(`http://localhost:${PORT}/api/sync-student`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ studentData, stats })
        });

        // Sync all attendance records
        for (const attendance of attendanceData) {
            await fetch(`http://localhost:${PORT}/api/sync-attendance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ attendanceRecord: attendance, studentData })
            });
        }

        // Sync all quiz records
        for (const quiz of quizData) {
            await fetch(`http://localhost:${PORT}/api/sync-quiz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quizRecord: quiz, studentData })
            });
        }

        res.json({
            success: true,
            message: `Đã đồng bộ thành công: ${attendanceData.length} lần điểm danh và ${quizData.length} kết quả quiz`
        });
    } catch (error) {
        console.error('Sync all failed:', error);
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════╗
║   🎓 Learning System Backend Server                ║
║                                                    ║
║   Server đang chạy tại: http://localhost:${PORT}     ║
║   Spreadsheet ID: ${SPREADSHEET_ID.substring(0, 20)}... ║
║                                                    ║
║   Endpoints:                                       ║
║   - GET  /api/test-connection                      ║
║   - POST /api/initialize-sheets                    ║
║   - POST /api/sync-student                         ║
║   - POST /api/sync-attendance                      ║
║   - POST /api/sync-quiz                            ║
║   - POST /api/sync-all                             ║
║                                                    ║
║   Mở trình duyệt: http://localhost:${PORT}           ║
╚════════════════════════════════════════════════════╝
    `);
});
