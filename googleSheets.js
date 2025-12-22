// Google Sheets Integration - Backend API Version
// Tự động phát hiện URL backend (local hoặc production)
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:3000/api'
    : window.location.origin + '/api';

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
    console.log('🔄 Bắt đầu đồng bộ:', type, data);
    
    if (!isGoogleSheetsConfigured()) {
        console.log('⚠️ Google Sheets chưa được cấu hình');
        return; // Không làm gì nếu chưa cấu hình
    }
    
    if (!studentData) {
        console.error('❌ Thiếu thông tin studentData');
        return false;
    }
    
    try {
        if (type === 'attendance') {
            console.log('📋 Đồng bộ điểm danh...');
            await syncAttendanceToSheets(data, studentData);
            console.log('✅ Đồng bộ điểm danh thành công');
        } else if (type === 'quiz') {
            console.log('📝 Đồng bộ quiz...');
            await syncQuizToSheets(data, studentData);
            console.log('✅ Đồng bộ quiz thành công');
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
        console.log('👤 Cập nhật thông tin học sinh...', stats);
        await syncStudentToSheets(studentData, stats);
        console.log('✅ Cập nhật thông tin học sinh thành công');
        
        return true;
    } catch (error) {
        console.error('❌ Lỗi tự động đồng bộ:', error);
        console.error('Chi tiết lỗi:', error.message);
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
