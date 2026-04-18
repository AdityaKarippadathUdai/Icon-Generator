from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.model import generate_icon
from app.schemas import GenerateRequest, GenerateResponse

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="AI Icon Generator")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate-icon", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    images = generate_icon(
        prompt=request.prompt,
        style=request.style,
        num_images=request.num_images,
        seed=request.seed,
    )
    return GenerateResponse(images=images)