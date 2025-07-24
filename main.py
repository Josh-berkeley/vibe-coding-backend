from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import openai
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Store generated apps in memory
shared_apps = {}

class PromptInput(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"message": "Vibe Coding API is running!"}

@app.post("/generate")
async def generate_code(data: PromptInput):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user", 
                "content": f"""Create a single HTML file web app for: {data.prompt}
                
Requirements:
- Complete HTML file with embedded CSS and JavaScript
- Functional and interactive
- Clean, simple design
- No external dependencies
- Use localStorage if data persistence needed

Return only the HTML code, nothing else."""
            }],
            max_tokens=2000
        )
        
        code = response.choices[0].message.content
        share_id = str(uuid.uuid4())[:8]
        shared_apps[share_id] = code
        
        return {
            "code": code,
            "share_id": share_id,
            "share_url": f"/share/{share_id}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/share/{share_id}")
async def get_shared_app(share_id: str):
    if share_id in shared_apps:
        return HTMLResponse(content=shared_apps[share_id])
    return HTMLResponse(content="<h1>App not found</h1>")
