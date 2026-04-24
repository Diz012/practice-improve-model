import os
import json
import re
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QuizRequest(BaseModel):
    mssv: str
    mon_hoc: str
    ly_do: str

# Khởi tạo client Groq - Nhớ bảo mật API Key của bạn nhé!
client = client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_study_hours(ly_do):
    """Hàm phụ để trích xuất số giờ tự học từ chuỗi văn bản."""
    match = re.search(r'(\d+)', ly_do)
    return int(match.group(1)) if match else 100 # Mặc định 100 nếu không tìm thấy số

def generate_quiz(mssv, mon_hoc, ly_do_rot):
    # Xác định số lượng câu hỏi dựa trên logic trong file
    study_hours = extract_study_hours(ly_do_rot)
    num_questions = 20
    
    level_questions = 'khó' # Mặc định
    if study_hours < 20 or "không có đề ôn tập" in ly_do_rot.lower():
        level_questions = 'dễ'
    elif study_hours < 40:
        level_questions = 'trung bình'
    elif study_hours < 60:
        level_questions = 'khó'

    prompt = f"""
    Thông tin:
    - MSSV: {mssv}
    - Môn học: {mon_hoc}
    - Lý do rớt: {ly_do_rot} (Thời gian tự học: {study_hours}h)

    Hãy tạo đúng chính xác 30 câu hỏi trắc nghiệm cho môn {mon_hoc}. 
    Yêu cầu:
    1. Trả về đúng 30 đối tượng trong danh sách 'danh_sach_cau_hoi'.
    2. Mức độ: {level_questions}.
    3. Định dạng JSON nghiêm ngặt.
    4. Có thể tham khảo trên trang eduquiz.vn
    (Không được trả về ít hơn hoặc nhiều hơn 30 câu). 
    
    Yêu cầu trả về duy nhất một đối tượng JSON có cấu trúc như sau:
    {{
        "danh_sach_cau_hoi": [
            {{
                "cau_hoi": "Nội dung câu hỏi...",
                "dap_an": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                "lua_chon_dung": "Nguyên văn nội dung của đáp án đúng",
                "giai_thich": "..."
            }}
        ]
    }}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Bạn là trợ lý học thuật. Chỉ trả về JSON chứa danh sách câu hỏi."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )

        data = json.loads(chat_completion.choices[0].message.content)
        max_retries = 2 # Thử lại nếu không đủ số lượng
        for attempt in range(max_retries):
            chat_completion = client.chat.completions.create(
                # ... cấu hình messages ...
            )
            
            data = json.loads(chat_completion.choices[0].message.content)
            questions = data.get("danh_sach_cau_hoi", [])
            
            if len(questions) == 20:
                return data
            else:
                print(f"Lần {attempt+1}: Model tạo ra {len(questions)} câu, đang thử lại...")
        return data

    except Exception as e:
        return {"error": str(e)}

@app.post("/generate-quiz")
async def api_generate_quiz(request: QuizRequest):
    # Gọi hàm generate_quiz của bạn ở đây
    result = generate_quiz(request.mssv, request.mon_hoc, request.ly_do)
    return result
