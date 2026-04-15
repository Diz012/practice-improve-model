import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# Khởi tạo client Groq
# Lưu ý: API Key sẽ được lấy từ môi trường (Environment Variable) khi deploy
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class StudentData(BaseModel):
    student_id: str  
    concerns: str    # Vấn đề cụ thể (vắng học, điểm thấp, tâm lý...)

@app.post("/get-advice")
async def get_advisor_advice(data: StudentData):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là một AI hỗ trợ cố vấn học tập tìm giải pháp hỗ trợ cải thiện tình hình học tập của sinh viên."
                        "Hãy phân tích các vấn đề của sinh viên và đưa ra lời khuyên cụ thể."
                        "Cần đồng cảm và có tính thực tiễn cao cho giảng viên cố vấn."
                        "Loại bỏ các kí tự không cần thiết"
                    ),
                },
                {
                    "role": "user",
                    "content": f"Vấn đề cần tư vấn: {data.concerns}",
                }
            ],
            model="llama-3.3-70b-versatile", # Model mạnh nhất của Groq hiện tại
        )
        return {
            "student_id": data.student_id
            "analysis": chat_completion.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
