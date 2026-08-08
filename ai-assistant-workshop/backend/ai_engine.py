import json
import os
try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None
from .tools import get_current_weather, calculate_expression, AVAILABLE_FUNCTIONS
from .rag_engine import RAGEngine

class GeminiAIEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Do not raise here; allow factory to choose fallback engine
            self.client = None
            self.rag = RAGEngine()
            print("[GeminiAIEngine] GEMINI_API_KEY không có — client không được khởi tạo.")
            return
        if genai is None:
            raise ModuleNotFoundError(
                "Package 'google-genai' không được cài. Chạy: pip install google-genai or pip install -r backend/requirements.txt"
            )

        self.client = genai.Client(api_key=api_key)
        self.rag = RAGEngine()

    async def generate_chat_stream(self, user_message: str, page_context: dict = None):
        rag_context = self.rag.query_context(user_message)
        
        system_instruction = f"""
        Bạn là một Trợ lý AI Thông minh hỗ trợ người dùng trên Website.
        Thông tin trang web người dùng đang xem:
        - URL: {page_context.get('url', 'N/A') if page_context else 'N/A'}
        - Tiêu đề trang: {page_context.get('title', 'N/A') if page_context else 'N/A'}

        Tri thức nội bộ tra cứu được (RAG):
        {rag_context if rag_context else 'Không có dữ liệu tri thức nội bộ khớp.'}

        Hãy trả lời ngắn gọn, lịch sự, chính xác.
        """

        chat = self.client.chats.create(
            model="gemini-3.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[get_current_weather, calculate_expression],
                temperature=0.7
            )
        )
        
        response = chat.send_message_stream(user_message)

        for chunk in response:
            if chunk.function_calls:
                for fn_call in chunk.function_calls:
                    fn_name = fn_call.name
                    fn_args = fn_call.args
                    
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': fn_name, 'args': fn_args}, ensure_ascii=False)}\n\n"
                    
                    if fn_name in AVAILABLE_FUNCTIONS:
                        tool_result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                    else:
                        tool_result = "Lỗi: Không tìm thấy function."

                    follow_up = chat.send_message_stream(
                        [types.Part.from_function_response(
                            name=fn_name,
                            response={'result': tool_result}
                        )]
                    )
                    for follow_chunk in follow_up:
                        if follow_chunk.text:
                            yield f"data: {json.dumps({'type': 'text_delta', 'content': follow_chunk.text}, ensure_ascii=False)}\n\n"
                    return

            if chunk.text:
                yield f"data: {json.dumps({'type': 'text_delta', 'content': chunk.text}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"


class MockAIEngine:
    """Fallback AI engine used when Gemini API key or SDK is unavailable.
    Implements the same async generator interface `generate_chat_stream`.
    """
    def __init__(self):
        self.name = "mock"

    async def generate_chat_stream(self, user_message: str, page_context: dict = None):
        # Simple fallback: stream a short canned response and finish
        intro = (
            "Xin chào! AI engine đang hoạt động ở chế độ mô phỏng (fallback)."
            " Hãy thiết lập GEMINI_API_KEY để dùng thực thi." 
        )
        yield f"data: {json.dumps({'type': 'text_delta', 'content': intro}, ensure_ascii=False)}\n\n"
        # Echo the user message as a helpful placeholder
        echo = f"(Fallback) Bạn đã hỏi: {user_message}"
        yield f"data: {json.dumps({'type': 'text_delta', 'content': echo}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


def create_ai_engine():
    """Factory: return a working AI engine instance. If Gemini configured and SDK present,
    return `GeminiAIEngine`, otherwise return `MockAIEngine`.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and genai is not None:
        try:
            return GeminiAIEngine()
        except Exception:
            # Fall back to mock on any unexpected error
            return MockAIEngine()
    return MockAIEngine()