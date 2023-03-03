# import whisper

# model = whisper.load_model("base")
# audio = "test_whisper/l38kg-w9041.opus"
# result = model.transcribe(audio)
# print(result["text"])
from fastapi import FastAPI
from app.api import api
app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Server is running'}


app.include_router(api.router)