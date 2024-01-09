from fastapi import FastAPI
from fastapi.responses import HTMLResponse,FileResponse
from fastapi import Request
from pydantic import BaseModel # for request body validation and request body parsing
from fastapi.staticfiles import StaticFiles # static files serving
app = FastAPI()

# youtube to audio converter
from pytube import YouTube
import os

# dotenv
from dotenv import load_dotenv
load_dotenv()
OpenAI_API_Key = os.getenv("OpenAI_API_Key")
# open AI
from openai import OpenAI
client = OpenAI(api_key=OpenAI_API_Key)

# serving static files
app.mount("/audios", StaticFiles(directory="audios"), name="audios")

@app.get("/")
async def root():
    body="<h1>Python Fast API Server for StudyMate Microservices</h1>"
    return HTMLResponse(content=body, status_code=200)

# Pydantic for request body validation and request body parsing
class YoutubeModel(BaseModel):
    link:str
    
@app.post("/youtube-to-audio")
async def youtubeVideoToAudio(youtubemodel:YoutubeModel):
    destination ="audios"
    # linkName=youtubemodel.link.split("/")[-1]
    linkName=youtubemodel.link.split("=")[1]
    filename=linkName+".mp3"
    host="http://localhost:8000"
    # check if the file is already exits
    if(os.path.isfile(os.path.join(destination, filename))):
        return {"status":"success", "message":"audio already exists","filename":filename}
    
    proxy = {"http": "http://127.0.0.1", "https": "https://127.0.0.1"}
    
    # yt = YouTube(youtubemodel.link,proxies=proxy)
    yt = YouTube(youtubemodel.link)
    
    # yt.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    video = yt.streams.filter(only_audio = True).first()
    out_file = video.download(output_path = destination)
    os.rename(out_file, os.path.join(destination, filename))
    return {"status":"success", "message":"audio downloaded","filename":filename}

@app.get("/audio/transcripion/{filename}")
async def transcription(filename:str):
    audio_file= open("audios/"+filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcript.text