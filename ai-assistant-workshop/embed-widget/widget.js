(function() {
    const hostDiv = document.createElement('div');
    hostDiv.id = 'ai-assistant-widget-root';
    document.body.appendChild(hostDiv);

    const shadow = hostDiv.attachShadow({ mode: 'open' });

    const style = document.createElement('style');
    style.textContent = `
        /* Import font chữ hiện đại */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }

        /* Nút Chat Bubble - Gradient chuyển động */
        .chat-bubble {
            position: fixed; bottom: 30px; right: 30px; width: 65px; height: 65px;
            border-radius: 50%; 
            background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
            color: white; display: flex; justify-content: center; align-items: center;
            font-size: 30px; cursor: pointer; 
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.4);
            z-index: 999999; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        @keyframes gradientShift { 
            0% {background-position: 0% 50%;} 
            50% {background-position: 100% 50%;} 
            100% {background-position: 0% 50%;} 
        }
        .chat-bubble:hover { transform: scale(1.1) translateY(-5px); box-shadow: 0 15px 35px rgba(139, 92, 246, 0.6); }

        /* Khung Chat - Glassmorphism thực thụ */
        .chat-window {
            position: fixed; bottom: 110px; right: 30px; width: 380px; height: 550px;
            background: rgba(17, 24, 39, 0.75); /* Nền tối, trong suốt */
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            display: none; flex-direction: column; overflow: hidden; z-index: 999999;
            /* Animation trượt lên */
            opacity: 0; transform: translateY(20px); transition: all 0.4s ease;
        }
        .chat-window.open { display: flex; opacity: 1; transform: translateY(0); }

        /* Phần Header */
        .header { 
            background: rgba(255, 255, 255, 0.03); 
            padding: 18px 20px; font-weight: 600; font-size: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08); 
            display: flex; justify-content: space-between; align-items: center; 
        }
        .header span:first-child { 
            background: linear-gradient(to right, #60a5fa, #c084fc); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        }
        .close-btn { cursor: pointer; color: #9ca3af; font-size: 20px; transition: color 0.2s; }
        .close-btn:hover { color: #f87171; }

        /* Vùng hiển thị tin nhắn */
        .body { 
            flex: 1; padding: 20px; overflow-y: auto; display: flex; 
            flex-direction: column; gap: 16px; scroll-behavior: smooth; 
        }
        .body::-webkit-scrollbar { width: 6px; }
        .body::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }

        /* Cấu trúc tin nhắn */
        .msg { 
            padding: 12px 16px; border-radius: 18px; font-size: 14.5px; 
            max-width: 82%; line-height: 1.5; 
            animation: fadeIn 0.3s ease; 
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .msg.user { 
            background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; 
            align-self: flex-end; border-bottom-right-radius: 4px; 
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); 
        }
        .msg.assistant { 
            background: rgba(255, 255, 255, 0.06); color: #e2e8f0; 
            align-self: flex-start; border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
        }

        /* Phần Footer nhập text */
        .footer { 
            padding: 16px; background: rgba(0, 0, 0, 0.2); display: flex; gap: 10px; 
            border-top: 1px solid rgba(255, 255, 255, 0.05); 
        }
        .footer input { 
            flex: 1; background: rgba(255, 255, 255, 0.05); 
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; 
            padding: 12px 16px; color: white; font-size: 14.5px; outline: none; transition: all 0.3s; 
        }
        .footer input:focus { 
            border-color: #8b5cf6; background: rgba(255, 255, 255, 0.08); 
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2); 
        }
        .footer input::placeholder { color: #64748b; }
        .footer button { 
            background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; 
            border: none; border-radius: 12px; padding: 0 18px; font-weight: 600; 
            cursor: pointer; transition: all 0.2s; 
        }
        .footer button:hover { opacity: 0.9; transform: scale(1.05); }
    `;
    shadow.appendChild(style);

    const widgetContainer = document.createElement('div');
    widgetContainer.innerHTML = `
        <div class="chat-bubble" id="toggleBtn">💬</div>
        <div class="chat-window" id="chatwin">
            <div class="header">
                <span>🤖 Gemini AI Assistant</span>
                <span class="close-btn" id="closeBtn">✕</span>
            </div>
            <div class="body" id="msgContainer">
                <div class="msg assistant">Xin chào! Tôi có thể giúp gì cho bạn trên trang web này?</div>
            </div>
            <div class="footer">
                <input type="text" id="widgetInput" placeholder="Nhập câu hỏi...">
                <button id="widgetSendBtn">Gửi</button>
            </div>
        </div>
    `;
    shadow.appendChild(widgetContainer);

    const toggleBtn = shadow.getElementById('toggleBtn');
    const closeBtn = shadow.getElementById('closeBtn');
    const chatwin = shadow.getElementById('chatwin');
    const inputEl = shadow.getElementById('widgetInput');
    const sendBtn = shadow.getElementById('widgetSendBtn');
    const msgContainer = shadow.getElementById('msgContainer');

    toggleBtn.onclick = () => chatwin.classList.toggle('open');
    closeBtn.onclick = () => chatwin.classList.remove('open');

    function appendWidgetMsg(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${role}`;
        msgDiv.innerText = text;
        msgContainer.appendChild(msgDiv);
        msgContainer.scrollTop = msgContainer.scrollHeight;
        return msgDiv;
    }

    async function handleSend() {
        const text = inputEl.value.trim();
        if (!text) return;

        appendWidgetMsg('user', text);
        inputEl.value = '';

        const aiMsgEl = appendWidgetMsg('assistant', 'Đang suy nghĩ...');
        const pageContext = { url: window.location.href, title: document.title };

        try {
            const res = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, page_context: pageContext })
            });

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
                                appendWidgetMsg('tool', `⚙️ Đang thực thi công cụ: ${data.name}`);
                            } else if (data.type === 'text_delta') {
                                if (aiMsgEl.innerText === 'Đang suy nghĩ...') fullText = "";
                                fullText += data.content;
                                aiMsgEl.innerText = fullText;
                            }
                        } catch(e) {}
                    }
                }
            }
        } catch(err) {
            aiMsgEl.innerText = '❌ Lỗi kết nối AI Server!';
        }
    }

    sendBtn.onclick = handleSend;
    inputEl.onkeypress = (e) => { if(e.key === 'Enter') handleSend(); };
})();