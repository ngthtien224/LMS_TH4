// Dữ liệu câu hỏi quiz
const quizQuestions = [
    {
        question: "HTML là viết tắt của gì?",
        options: [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Home Tool Markup Language",
            "Hyperlinks and Text Markup Language"
        ],
        correct: 0
    },
    {
        question: "CSS được sử dụng để làm gì?",
        options: [
            "Tạo cơ sở dữ liệu",
            "Tạo logic cho website",
            "Tạo giao diện và định dạng cho website",
            "Quản lý server"
        ],
        correct: 2
    },
    {
        question: "JavaScript là ngôn ngữ lập trình gì?",
        options: [
            "Ngôn ngữ biên dịch",
            "Ngôn ngữ thông dịch",
            "Ngôn ngữ assembly",
            "Ngôn ngữ máy"
        ],
        correct: 1
    },
    {
        question: "Thẻ nào dùng để tạo link trong HTML?",
        options: [
            "<link>",
            "<a>",
            "<href>",
            "<url>"
        ],
        correct: 1
    },
    {
        question: "Cách nào đúng để khai báo biến trong JavaScript?",
        options: [
            "variable x = 5;",
            "var x = 5;",
            "v x = 5;",
            "dim x = 5;"
        ],
        correct: 1
    },
    {
        question: "Thuộc tính nào để thay đổi màu chữ trong CSS?",
        options: [
            "text-color",
            "font-color",
            "color",
            "text-style"
        ],
        correct: 2
    },
    {
        question: "Phương thức nào để in ra console trong JavaScript?",
        options: [
            "console.write()",
            "console.print()",
            "console.log()",
            "console.output()"
        ],
        correct: 2
    },
    {
        question: "Bootstrap là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một framework CSS",
            "Một database",
            "Một web server"
        ],
        correct: 1
    },
    {
        question: "Thẻ nào dùng để nhúng JavaScript vào HTML?",
        options: [
            "<javascript>",
            "<js>",
            "<script>",
            "<code>"
        ],
        correct: 2
    },
    {
        question: "Git là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một hệ thống quản lý phiên bản",
            "Một framework",
            "Một database"
        ],
        correct: 1
    },
    {
        question: "HTTP là viết tắt của gì?",
        options: [
            "Hyper Text Transfer Protocol",
            "High Tech Transfer Protocol",
            "Home Tool Transfer Protocol",
            "Hyperlinks Transfer Protocol"
        ],
        correct: 0
    },
    {
        question: "Responsive design là gì?",
        options: [
            "Thiết kế nhanh",
            "Thiết kế tương tác",
            "Thiết kế thích ứng với nhiều thiết bị",
            "Thiết kế đơn giản"
        ],
        correct: 2
    },
    {
        question: "JSON là viết tắt của gì?",
        options: [
            "JavaScript Object Notation",
            "Java Source Object Notation",
            "JavaScript Online Notation",
            "Java Serialized Object Notation"
        ],
        correct: 0
    },
    {
        question: "API là viết tắt của gì?",
        options: [
            "Application Programming Interface",
            "Advanced Programming Interface",
            "Application Process Integration",
            "Advanced Process Interface"
        ],
        correct: 0
    },
    {
        question: "LocalStorage trong JavaScript dùng để làm gì?",
        options: [
            "Lưu trữ dữ liệu trên server",
            "Lưu trữ dữ liệu trên trình duyệt",
            "Tạo database",
            "Gửi email"
        ],
        correct: 1
    },
    {
        question: "SQL là gì?",
        options: [
            "Ngôn ngữ lập trình web",
            "Ngôn ngữ truy vấn cơ sở dữ liệu",
            "Framework JavaScript",
            "Thư viện CSS"
        ],
        correct: 1
    },
    {
        question: "React là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một thư viện JavaScript để xây dựng giao diện",
            "Một database",
            "Một web server"
        ],
        correct: 1
    },
    {
        question: "Node.js là gì?",
        options: [
            "Một framework CSS",
            "Một môi trường chạy JavaScript phía server",
            "Một trình duyệt web",
            "Một database"
        ],
        correct: 1
    },
    {
        question: "GitHub là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một nền tảng lưu trữ và quản lý mã nguồn",
            "Một trình soạn thảo code",
            "Một framework"
        ],
        correct: 1
    },
    {
        question: "Cookie trong web development dùng để làm gì?",
        options: [
            "Tạo hình ảnh động",
            "Lưu trữ thông tin người dùng",
            "Tạo hiệu ứng",
            "Quản lý database"
        ],
        correct: 1
    },
    {
        question: "AJAX là viết tắt của gì?",
        options: [
            "Asynchronous JavaScript and XML",
            "Advanced JavaScript and XML",
            "Automatic JavaScript and XML",
            "Asynchronous Java and XML"
        ],
        correct: 0
    },
    {
        question: "Framework là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một bộ công cụ và thư viện hỗ trợ phát triển",
            "Một database",
            "Một trình duyệt"
        ],
        correct: 1
    },
    {
        question: "MongoDB là loại database gì?",
        options: [
            "SQL Database",
            "NoSQL Database",
            "Graph Database",
            "In-memory Database"
        ],
        correct: 1
    },
    {
        question: "TypeScript là gì?",
        options: [
            "Một ngôn ngữ mới hoàn toàn",
            "Một superset của JavaScript có thêm kiểu dữ liệu",
            "Một framework",
            "Một database"
        ],
        correct: 1
    },
    {
        question: "REST API là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một kiểu kiến trúc API",
            "Một database",
            "Một framework"
        ],
        correct: 1
    },
    {
        question: "Webpack là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một công cụ đóng gói module",
            "Một database",
            "Một framework CSS"
        ],
        correct: 1
    },
    {
        question: "NPM là viết tắt của gì?",
        options: [
            "Node Package Manager",
            "New Programming Method",
            "Network Protocol Manager",
            "Node Program Manager"
        ],
        correct: 0
    },
    {
        question: "SASS/SCSS là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một CSS preprocessor",
            "Một JavaScript framework",
            "Một database"
        ],
        correct: 1
    },
    {
        question: "Docker là gì?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một nền tảng container hóa ứng dụng",
            "Một database",
            "Một text editor"
        ],
        correct: 1
    },
    {
        question: "Agile là gì trong phát triển phần mềm?",
        options: [
            "Một ngôn ngữ lập trình",
            "Một phương pháp quản lý dự án linh hoạt",
            "Một framework",
            "Một database"
        ],
        correct: 1
    }
];
