// Google Sheets Integration - Backend API Version
const API_BASE_URL = 'http://localhost:3000/api';

// Kiểm tra cấu hình Google Sheets (luôn trả về true vì backend đã cấu hình)
function isGoogleSheetsConfigured() {
    return true;
}

// Lưu cấu hình (không cần thiết nữa, backend đã có credentials)
function saveGoogleSheetsConfig(apiKey, spreadsheetId) {
    // No longer needed - server handles this
    return true;
}

// Xóa cấu hình (không cần thiết)
function clearGoogleSheetsConfig() {
    // No longer needed
    return true;
}

// Gọi Backend API
async function callBackendAPI(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Lỗi kết nối backend');
    }
    
    return await response.json();
}

// Khởi tạo Google Sheets với header
async function initializeGoogleSheets() {
    try {
        const result = await callBackendAPI('/initialize-sheets', 'POST');
        return result.success;
    } catch (error) {
        console.error('Lỗi khởi tạo Google Sheets:', error);
        throw error;
    }
}

// Đồng bộ thông tin học sinh
async function syncStudentToSheets(studentData, stats) {
    try {
        await callBackendAPI('/sync-student', 'POST', { studentData, stats });
        return true;
    } catch (error) {
        console.error('Lỗi đồng bộ thông tin học sinh:', error);
        throw error;
    }
}

// Đồng bộ điểm danh
async function syncAttendanceToSheets(attendanceRecord, studentData) {
    try {
        await callBackendAPI('/sync-attendance', 'POST', { attendanceRecord, studentData });
        return true;
    } catch (error) {
        console.error('Lỗi đồng bộ điểm danh:', error);
        throw error;
    }
}

// Đồng bộ kết quả quiz
async function syncQuizToSheets(quizRecord, studentData) {
    try {
        await callBackendAPI('/sync-quiz', 'POST', { quizRecord, studentData });
        return true;
    } catch (error) {
        console.error('Lỗi đồng bộ kết quả quiz:', error);
        throw error;
    }
}

// Đồng bộ toàn bộ dữ liệu
async function syncAllDataToSheets() {
    try {
        if (!studentData) {
            throw new Error('Chưa có thông tin học sinh');
        }
        
        // Tính thống kê
        const stats = {
            totalAttendance: attendanceData.length,
            totalQuizzes: quizData.length,
            averageScore: quizData.length > 0 
                ? Math.round(quizData.reduce((sum, q) => sum + q.score, 0) / quizData.length)
                : 0,
            highestScore: quizData.length > 0 
                ? Math.max(...quizData.map(q => q.score))
                : 0
        };
        
        // Gọi API đồng bộ toàn bộ
        const result = await callBackendAPI('/sync-all', 'POST', {
            studentData,
            attendanceData,
            quizData,
            stats
        });
        
        return result;
    } catch (error) {
        console.error('Lỗi đồng bộ toàn bộ dữ liệu:', error);
        throw error;
    }
}

// Đồng bộ tự động sau mỗi hành động
async function autoSyncToSheets(type, data) {
    if (!isGoogleSheetsConfigured()) {
        return; // Không làm gì nếu chưa cấu hình
    }
    
    try {
        if (type === 'attendance') {
            await syncAttendanceToSheets(data, studentData);
        } else if (type === 'quiz') {
            await syncQuizToSheets(data, studentData);
        }
        
        // Cập nhật thông tin học sinh
        const stats = {
            totalAttendance: attendanceData.length,
            totalQuizzes: quizData.length,
            averageScore: quizData.length > 0 
                ? Math.round(quizData.reduce((sum, q) => sum + q.score, 0) / quizData.length)
                : 0,
            highestScore: quizData.length > 0 
                ? Math.max(...quizData.map(q => q.score))
                : 0
        };
        await syncStudentToSheets(studentData, stats);
        
        return true;
    } catch (error) {
        console.error('Lỗi tự động đồng bộ:', error);
        // Không throw error để không làm gián đoạn ứng dụng
        return false;
    }
}

// Kiểm tra kết nối Google Sheets
async function testGoogleSheetsConnection() {
    try {
        const result = await callBackendAPI('/test-connection', 'GET');
        return result;
    } catch (error) {
        return { success: false, message: error.message };
    }
}

// Helper function - format date
function formatDate(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}
