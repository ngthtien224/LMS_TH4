// Lấy dữ liệu từ localStorage
let studentData = JSON.parse(localStorage.getItem('studentData')) || null;
let attendanceData = JSON.parse(localStorage.getItem('attendanceData')) || [];
let quizData = JSON.parse(localStorage.getItem('quizData')) || [];

// Quiz state
let currentQuizIndex = 0;
let currentQuestions = [];
let userAnswers = [];
let quizTimer = null;
let timeRemaining = 60;

// Khởi tạo app
document.addEventListener('DOMContentLoaded', function() {
    displayCurrentDate();
    checkStudentInfo();
    updateStatistics();
});

// Hiển thị ngày hiện tại
function displayCurrentDate() {
    const dateElement = document.getElementById('currentDate');
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    dateElement.textContent = now.toLocaleDateString('vi-VN', options);
}

// Kiểm tra thông tin học viên
function checkStudentInfo() {
    if (studentData) {
        showMainSections();
    } else {
        document.getElementById('studentInfoSection').style.display = 'block';
    }
}

// Lưu thông tin học viên
function saveStudentInfo() {
    const name = document.getElementById('studentName').value.trim();
    const id = document.getElementById('studentId').value.trim();
    
    if (!name || !id) {
        alert('Vui lòng nhập đầy đủ thông tin!');
        return;
    }
    
    studentData = { name, id, registeredDate: new Date().toISOString() };
    localStorage.setItem('studentData', JSON.stringify(studentData));
    
    showMainSections();
}

// Hiển thị các phần chính
function showMainSections() {
    document.getElementById('studentInfoSection').style.display = 'none';
    document.getElementById('attendanceSection').style.display = 'block';
    // document.getElementById('quizSection').style.display = 'block'; // ĐÃ TẮT QUIZ
    document.getElementById('statisticsSection').style.display = 'block';
    // Google Sheets section ẩn cho sinh viên
    
    // Hiển thị thông tin học viên
    document.getElementById('displayName').textContent = studentData.name;
    document.getElementById('displayId').textContent = studentData.id;
    
    checkTodayAttendance();
    // checkTodayQuiz(); // ĐÃ TẮT QUIZ
    displayAttendanceHistory();
    // displayQuizHistory(); // ĐÃ TẮT QUIZ
    // updateGoogleSheetsStatus(); - Ẩn cho sinh viên
}

// Kiểm tra điểm danh hôm nay
function checkTodayAttendance() {
    const today = getTodayDateString();
    const todayAttendance = attendanceData.find(a => a.date === today);
    
    const statusDiv = document.getElementById('attendanceStatus');
    const attendanceBtn = document.getElementById('attendanceBtn');
    
    if (todayAttendance) {
        statusDiv.className = 'status-message success';
        statusDiv.innerHTML = `✓ Bạn đã điểm danh hôm nay lúc ${todayAttendance.time}`;
        attendanceBtn.disabled = true;
        attendanceBtn.textContent = '✓ Đã điểm danh';
    } else {
        statusDiv.className = 'status-message info';
        statusDiv.innerHTML = '⏰ Bạn chưa điểm danh hôm nay';
        attendanceBtn.disabled = false;
        attendanceBtn.textContent = '✓ Điểm danh';
    }
}

// Điểm danh
function markAttendance() {
    const today = getTodayDateString();
    const now = new Date();
    const time = now.toLocaleTimeString('vi-VN');
    
    const attendance = {
        date: today,
        time: time,
        timestamp: now.toISOString()
    };
    
    attendanceData.push(attendance);
    localStorage.setItem('attendanceData', JSON.stringify(attendanceData));
    
    checkTodayAttendance();
    displayAttendanceHistory();
    updateStatistics();
    
    // Tự động đồng bộ Google Sheets
    autoSyncToSheets('attendance', attendance);
    
    // Animation
    const btn = document.getElementById('attendanceBtn');
    btn.classList.add('pulse');
    setTimeout(() => btn.classList.remove('pulse'), 1000);
}

// Hiển thị lịch sử điểm danh
function displayAttendanceHistory() {
    const historyDiv = document.getElementById('attendanceHistory');
    
    if (attendanceData.length === 0) {
        historyDiv.innerHTML = '<p style="text-align: center; color: #999;">Chưa có lịch sử điểm danh</p>';
        return;
    }
    
    const sortedData = [...attendanceData].reverse();
    historyDiv.innerHTML = sortedData.map(item => `
        <div class="history-item fade-in">
            <span class="history-date">📅 ${formatDate(item.date)}</span>
            <span class="history-time">🕐 ${item.time}</span>
        </div>
    `).join('');
}

// Kiểm tra quiz hôm nay
function checkTodayQuiz() {
    const today = getTodayDateString();
    const todayQuiz = quizData.find(q => q.date === today);
    
    const statusDiv = document.getElementById('quizStatus');
    const startBtn = document.getElementById('startQuizBtn');
    const resultDiv = document.getElementById('quizResult');
    
    if (todayQuiz) {
        statusDiv.className = 'status-message success';
        statusDiv.innerHTML = `✓ Bạn đã hoàn thành quiz hôm nay - Điểm: ${todayQuiz.score}/100`;
        startBtn.style.display = 'none';
        resultDiv.style.display = 'none';
    } else {
        statusDiv.className = 'status-message info';
        statusDiv.innerHTML = '📝 Bạn chưa làm quiz hôm nay';
        startBtn.style.display = 'inline-block';
    }
}

// Bắt đầu quiz
function startQuiz() {
    // Lấy 5 câu hỏi ngẫu nhiên
    const allQuestions = [...quizQuestions];
    currentQuestions = [];
    
    for (let i = 0; i < 5; i++) {
        const randomIndex = Math.floor(Math.random() * allQuestions.length);
        currentQuestions.push(allQuestions[randomIndex]);
        allQuestions.splice(randomIndex, 1);
    }
    
    currentQuizIndex = 0;
    userAnswers = [];
    timeRemaining = 60;
    
    document.getElementById('quizStatus').style.display = 'none';
    document.getElementById('startQuizBtn').style.display = 'none';
    document.getElementById('quizContainer').style.display = 'block';
    document.getElementById('quizResult').style.display = 'none';
    
    displayQuestion();
    startTimer();
}

// Hiển thị câu hỏi
function displayQuestion() {
    const question = currentQuestions[currentQuizIndex];
    
    document.getElementById('currentQuestion').textContent = currentQuizIndex + 1;
    document.getElementById('totalQuestions').textContent = currentQuestions.length;
    document.getElementById('questionText').textContent = question.question;
    
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = question.options.map((option, index) => `
        <div class="option" onclick="selectOption(${index})">
            ${String.fromCharCode(65 + index)}. ${option}
        </div>
    `).join('');
    
    const nextBtn = document.getElementById('nextBtn');
    if (currentQuizIndex === currentQuestions.length - 1) {
        nextBtn.textContent = 'Hoàn thành Quiz';
    } else {
        nextBtn.textContent = 'Câu tiếp theo →';
    }
    
    nextBtn.disabled = true;
}

// Chọn đáp án
function selectOption(optionIndex) {
    // Xóa selection cũ
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    // Thêm selection mới
    document.querySelectorAll('.option')[optionIndex].classList.add('selected');
    
    userAnswers[currentQuizIndex] = optionIndex;
    document.getElementById('nextBtn').disabled = false;
}

// Câu hỏi tiếp theo
function nextQuestion() {
    if (userAnswers[currentQuizIndex] === undefined) {
        alert('Vui lòng chọn đáp án!');
        return;
    }
    
    currentQuizIndex++;
    
    if (currentQuizIndex < currentQuestions.length) {
        displayQuestion();
        // Reset timer for new question
        timeRemaining = 60;
    } else {
        finishQuiz();
    }
}

// Timer
function startTimer() {
    quizTimer = setInterval(() => {
        timeRemaining--;
        document.getElementById('timeLeft').textContent = timeRemaining;
        
        if (timeRemaining <= 0) {
            clearInterval(quizTimer);
            if (currentQuizIndex < currentQuestions.length) {
                alert('Hết thời gian! Chuyển sang câu tiếp theo.');
                currentQuizIndex++;
                if (currentQuizIndex < currentQuestions.length) {
                    timeRemaining = 60;
                    displayQuestion();
                } else {
                    finishQuiz();
                }
            }
        }
    }, 1000);
}

// Hoàn thành quiz
function finishQuiz() {
    clearInterval(quizTimer);
    
    // Tính điểm
    let correctCount = 0;
    currentQuestions.forEach((question, index) => {
        if (userAnswers[index] === question.correct) {
            correctCount++;
        }
    });
    
    const score = Math.round((correctCount / currentQuestions.length) * 100);
    
    // Lưu kết quả
    const today = getTodayDateString();
    const quizResult = {
        date: today,
        score: score,
        correctAnswers: correctCount,
        totalQuestions: currentQuestions.length,
        timestamp: new Date().toISOString()
    };
    
    quizData.push(quizResult);
    localStorage.setItem('quizData', JSON.stringify(quizData));
    
    // Tự động đồng bộ Google Sheets
    autoSyncToSheets('quiz', quizResult);
    
    // Hiển thị kết quả
    document.getElementById('quizContainer').style.display = 'none';
    document.getElementById('quizResult').style.display = 'block';
    document.getElementById('finalScore').textContent = score;
    document.getElementById('correctAnswers').textContent = correctCount;
    document.getElementById('totalQuestionsResult').textContent = currentQuestions.length;
    
    const resultMessage = document.getElementById('resultMessage');
    if (score >= 80) {
        resultMessage.textContent = '🎉 Xuất sắc! Bạn đã làm rất tốt!';
        resultMessage.style.color = '#50c878';
    } else if (score >= 60) {
        resultMessage.textContent = '👍 Khá tốt! Tiếp tục cố gắng!';
        resultMessage.style.color = '#f39c12';
    } else {
        resultMessage.textContent = '💪 Cần cố gắng thêm! Đừng bỏ cuộc!';
        resultMessage.style.color = '#e74c3c';
    }
    
    checkTodayQuiz();
    displayQuizHistory();
    updateStatistics();
}

// Hiển thị lịch sử quiz
function displayQuizHistory() {
    const historyDiv = document.getElementById('quizHistory');
    
    if (quizData.length === 0) {
        historyDiv.innerHTML = '<p style="text-align: center; color: #999;">Chưa có lịch sử làm quiz</p>';
        return;
    }
    
    const sortedData = [...quizData].reverse();
    historyDiv.innerHTML = sortedData.map(item => {
        const scoreClass = item.score >= 80 ? 'high' : item.score >= 60 ? 'medium' : 'low';
        return `
            <div class="history-item fade-in">
                <div>
                    <span class="history-date">📅 ${formatDate(item.date)}</span>
                    <br>
                    <small>${item.correctAnswers}/${item.totalQuestions} câu đúng</small>
                </div>
                <span class="history-score ${scoreClass}">
                    ${item.score} điểm
                </span>
            </div>
        `;
    }).join('');
}

// Cập nhật thống kê
function updateStatistics() {
    // Chỉ cập nhật attendance, quiz đã tắt
    const attendanceElement = document.getElementById('totalAttendance');
    if (attendanceElement) {
        attendanceElement.textContent = attendanceData.length;
    }
    
    // COMMENT: Các element quiz đã bị tắt, không cập nhật nữa
    /*
    document.getElementById('totalQuizzes').textContent = quizData.length;
    
    if (quizData.length > 0) {
        const totalScore = quizData.reduce((sum, q) => sum + q.score, 0);
        const avgScore = Math.round(totalScore / quizData.length);
        document.getElementById('averageScore').textContent = avgScore;
        
        const highScore = Math.max(...quizData.map(q => q.score));
        document.getElementById('highestScore').textContent = highScore;
    } else {
        document.getElementById('averageScore').textContent = '0';
        document.getElementById('highestScore').textContent = '0';
    }
    */
}

// Đặt lại dữ liệu
function resetData() {
    if (confirm('Bạn có chắc muốn xóa toàn bộ dữ liệu? Hành động này không thể hoàn tác!')) {
        localStorage.clear();
        location.reload();
    }
}

// Xuất dữ liệu
function exportData() {
    const exportObj = {
        student: studentData,
        attendance: attendanceData,
        quizzes: quizData,
        exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportObj, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `learning-data-${getTodayDateString()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    alert('Đã xuất dữ liệu thành công!');
}

// Utility functions
function getTodayDateString() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

function formatDate(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}

// ========== GOOGLE SHEETS UI FUNCTIONS ==========

// Hiển thị/Ẩn phần Google Sheets
function toggleGoogleSheets() {
    const section = document.getElementById('googleSheetsSection');
    if (section.style.display === 'none') {
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
    } else {
        section.style.display = 'none';
    }
}

// Cập nhật trạng thái kết nối Google Sheets
function updateGoogleSheetsStatus() {
    // Backend đã cấu hình sẵn, không cần UI phức tạp
    const statusText = document.getElementById('sheetsStatusText');
    statusText.innerHTML = '✅ Backend server đang kết nối với Google Sheets';
}

// Lưu cấu hình Google Sheets (không cần thiết nữa)
function saveGoogleSheetsConfiguration() {
    alert('Backend server đã được cấu hình sẵn với credentials!');
}

// Kiểm tra kết nối
async function testConnection() {
    const resultDiv = document.getElementById('syncResult');
    resultDiv.innerHTML = '<div class="status-message info">🔌 Đang kiểm tra kết nối...</div>';
    
    const result = await testGoogleSheetsConnection();
    
    if (result.success) {
        resultDiv.innerHTML = `<div class="status-message success">✅ ${result.message}<br>📊 Sheet: ${result.sheetTitle || 'Connected'}</div>`;
    } else {
        resultDiv.innerHTML = `<div class="status-message" style="background: #f8d7da; color: #721c24; border-color: #f5c6cb;">❌ Lỗi: ${result.message}<br>⚠️ Đảm bảo backend server đang chạy!</div>`;
    }
    
    setTimeout(() => {
        resultDiv.innerHTML = '';
    }, 5000);
}

// Xóa cấu hình (không cần thiết)
function clearConfiguration() {
    alert('Backend server quản lý credentials, không cần xóa!');
}

// Hiển thị form cấu hình (không cần thiết)
function showConfiguration() {
    alert('Backend server đã được cấu hình sẵn!');
}

// Đồng bộ toàn bộ dữ liệu
async function syncAllData() {
    const resultDiv = document.getElementById('syncResult');
    resultDiv.innerHTML = '<div class="status-message info">🔄 Đang đồng bộ dữ liệu...</div>';
    
    try {
        const result = await syncAllDataToSheets();
        resultDiv.innerHTML = `<div class="status-message success">✅ ${result.message}</div>`;
        
        setTimeout(() => {
            resultDiv.innerHTML = '';
        }, 5000);
    } catch (error) {
        resultDiv.innerHTML = `<div class="status-message" style="background: #f8d7da; color: #721c24; border-color: #f5c6cb;">❌ Lỗi: ${error.message}</div>`;
    }
}
