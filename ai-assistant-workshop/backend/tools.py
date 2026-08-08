import json
import datetime

def get_current_weather(location: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một thành phố."""
    return json.dumps({
        "location": location,
        "temperature": "28°C",
        "condition": "Nắng nhẹ, có mây",
        "humidity": "65%",
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }, ensure_ascii=False)

def calculate_expression(expression: str) -> str:
    """Thực hiện phép tính toán học an toàn."""
    try:
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Lỗi: Biểu thức chứa ký tự không hợp lệ."
        result = eval(expression)
        return json.dumps({"expression": expression, "result": result}, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi tính toán: {str(e)}"

AVAILABLE_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    "calculate_expression": calculate_expression
}