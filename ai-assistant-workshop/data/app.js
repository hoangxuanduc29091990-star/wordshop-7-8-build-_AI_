// Lấy các element từ HTML
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const msgContainer = document.getElementById('msgContainer');

// Hàm thêm tin nhắn vào giao diện
function appendMsg(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${role}`;
    msgDiv.innerText = text;
    msgContainer.appendChild(msgDiv);
    
    // Tự động cuộn xuống cuối cùng
    msgContainer.scrollTop = msgContainer.scrollHeight;
    return msgDiv;
}

// Xử lý gửi tin nhắn
async function handleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hiển thị tin nhắn người dùng
    appendMsg('user', text);
    chatInput.value = ''; // Xóa ô input

    // Khởi tạo bong bóng "Đang suy nghĩ..." cho AI
    const aiMsgEl = appendMsg('assistant', 'Đang suy nghĩ...');
    
    const pageContext = { url: window.location.href, title: document.title };

    try {
        // Gọi API tới FastAPI Server
        const res = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, page_context: pageContext })
        });

        // Đọc dữ liệu dạng SSE Stream trả về
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const lines = decoder.decode(value).split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.replace('data: ', '').trim();
                    if (jsonStr === '[DONE]') break;
                    try {
                        const data = JSON.parse(jsonStr);
                        if (data.type === 'tool_call') {
                            appendMsg('tool', `⚙️ Đang thực thi công cụ: ${data.name}`);
                        } else if (data.type === 'text_delta') {
                            // Xóa chữ "Đang suy nghĩ..." ở chunk đầu tiên
                            if (aiMsgEl.innerText === 'Đang suy nghĩ...') {
                                fullText = ""; 
                            }
                            fullText += data.content;
                            aiMsgEl.innerText = fullText; // Cập nhật text realtime
                        }
                    } catch(e) {
                        console.error("Lỗi phân tích JSON:", e);
                    }
                }
            }
        }
    } catch(err) {
        console.error("Lỗi kết nối Server:", err);
        aiMsgEl.innerText = '❌ Lỗi kết nối AI Server! Hãy chắc chắn rằng bạn đang bật Server (python main.py)';
    }
}

// Gắn sự kiện click và nhấn Enter
sendBtn.onclick = handleSend;
chatInput.onkeypress = (e) => { 
    if (e.key === 'Enter') handleSend(); 
};