import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# Khởi tạo client Groq
# Lưu ý: API Key sẽ được lấy từ môi trường (Environment Variable) khi deploy
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class StudentData(BaseModel):
    transcript: str  # Bảng điểm hoặc tình trạng học tập
    concerns: str    # Vấn đề cụ thể (vắng học, điểm thấp, tâm lý...)

@app.post("/get-advice")
async def get_advisor_advice(data: StudentData):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là một chuyên gia cố vấn học tập dày dạn kinh nghiệm. "
                        "Hãy phân tích dữ liệu sinh viên và đưa ra lời khuyên cụ thể, "
                        "đồng cảm và có tính thực tiễn cao cho giảng viên cố vấn."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Dữ liệu sinh viên: {data.transcript}\nVấn đề cần tư vấn: {data.concerns}",
                }
            ],
            model="llama-3.3-70b-versatile", # Model mạnh nhất của Groq hiện tại
        )
        return {"advice": chat_completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
