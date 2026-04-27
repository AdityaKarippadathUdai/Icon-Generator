# 🧩 AI Icon Generator

**Stable Diffusion · FastAPI · Docker**

Generate clean, minimalist icons from text prompts using Stable Diffusion v1.5.
This project provides a complete full-stack pipeline — model inference, prompt engineering, image post-processing, a REST API, and a web UI — optimized for low-VRAM (4 GB) GPUs.

---

## 🚀 Features

- **Text-to-Icon Generation** — describe any object; get a clean flat icon back
- **Three Style Presets** — `minimal`, `filled`, and `neon`, each injecting a different prompt fragment
- **Prompt Engineering Pipeline** — `BASE_PROMPT_TEMPLATE` automatically structures your input for icon-style SD outputs
- **Post-Processing Pipeline** — Otsu thresholding + Canny edge detection via OpenCV for sharper, high-contrast icons
- **Low-VRAM Optimised** — attention slicing, VAE slicing, and CPU offloading keep peak VRAM usage low enough for a 4 GB GPU
- **FastAPI Backend** — typed REST API with Pydantic validation, auto-generated `/docs`
- **Minimal Web UI** — HTML + vanilla JS frontend; no framework required
- **Docker Support** — single-command GPU container with CUDA 12.1

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Model | Stable Diffusion v1.5 (`.safetensors`) |
| Inference | Hugging Face `diffusers` |
| Validation | Pydantic v2 |
| Post-processing | Pillow + OpenCV (`opencv-python-headless`) |
| Frontend | HTML5 + Vanilla JS + CSS3 |
| Containerisation | Docker + NVIDIA CUDA 12.1 |

---

## 📁 Project Structure

```
icon-generator/
├── app/
│   ├── main.py          # FastAPI app — routes, static files, templates
│   ├── model.py         # Stable Diffusion pipeline — load, generate, encode
│   ├── pipeline.py      # Post-processing — threshold + edge detection
│   ├── schemas.py       # Pydantic request/response models
│   ├── config.py        # Constants — paths, prompt templates, style presets
│   ├── templates/
│   │   └── index.html   # Jinja2 HTML frontend
│   └── static/
│       ├── js/
│       │   └── app.js   # fetch API, DOM rendering, download handler
│       └── css/
│           └── style.css
│
├── models/              # Place your .safetensors model here (not in repo)
├── outputs/
│   ├── raw/             # Raw SD outputs (optional saving)
│   └── processed/       # Post-processed outputs (optional saving)
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚠️ Model Setup (Required)

The model file is **not included** in this repository due to size.

### Option A — SD v1.5 (default)

Download the pruned EMA-only weights from Hugging Face:

```
https://huggingface.co/runwayml/stable-diffusion-v1-5
```

Download file: `v1-5-pruned-emaonly.safetensors`

### Option B — DreamShaper v8 (recommended for icons)

DreamShaper produces cleaner, more stylised outputs for icon-style prompts:

```
https://civitai.com/models/4384/dreamshaper
```

Download file: `dreamshaper_8.safetensors`

### Place the model here

```
models/v1-5-pruned-emaonly.safetensors
```

Then update `MODEL_PATH` in `app/model.py` to the absolute path:

```python
MODEL_PATH = "/absolute/path/to/your/models/v1-5-pruned-emaonly.safetensors"
```

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/icon-generator.git
cd icon-generator
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install PyTorch with CUDA support

Install the GPU-enabled PyTorch wheel **before** the rest of the requirements.
Replace `cu121` with your CUDA version if different (check with `nvidia-smi`):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install remaining dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Open in browser

```
http://127.0.0.1:8000
```

---

## 🐳 Docker Setup

### Build the image

```bash
docker build -t icon-generator .
```

> **Note:** The `models/` directory is baked into the image at build time.
> For a lighter image, mount it at runtime instead (see below).

### Run with GPU

```bash
docker run --gpus all -p 8000:8000 icon-generator
```

### Run with a volume-mounted model (lighter image)

```bash
docker run --gpus all -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  icon-generator
```

---

## 🧪 API Reference

### `GET /`

Returns the HTML frontend (`index.html`).

---

### `POST /generate-icon`

Generate one or more icons from a text prompt.

**Request body (JSON):**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | `string` | ✅ | — | Object to generate (e.g. `"a camera"`) |
| `style` | `string` | ❌ | `"minimal"` | One of `minimal`, `filled`, `neon` |
| `num_images` | `int` | ❌ | `1` | Number of images to generate (1–4) |
| `seed` | `int` | ❌ | `null` | RNG seed for reproducibility |

**Example request:**

```bash
curl -X POST http://localhost:8000/generate-icon \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a lightning bolt",
    "style": "neon",
    "num_images": 2,
    "seed": 42
  }'
```

**Example response:**

```json
{
  "images": [
    "<base64-encoded-PNG>",
    "<base64-encoded-PNG>"
  ]
}
```

Each string in `images` is a base64-encoded PNG. Render directly in HTML:

```html
<img src="data:image/png;base64,<string>" />
```

**Validation errors (422):**

FastAPI returns a structured error if `num_images` is outside 1–4 or if required fields are missing.

---

## 🎨 Style Presets

Style presets are defined in `config.py` and injected directly into the prompt:

| Key | Injected fragment |
|---|---|
| `minimal` | `minimal linework, clean outlines, simple shapes, monochrome` |
| `filled` | `bold filled shapes, flat colors, solid design, no outlines` |
| `neon` | `neon glowing colors, dark background, vibrant electric hues, luminous edges` |

The full prompt is assembled as:

```
"A clean minimalist flat icon of {object}, {style}, vector style, black outline, white background"
```

---

## 🔬 Post-Processing Pipeline (`pipeline.py`)

Each generated image optionally passes through `process_image()`:

1. **Grayscale conversion** — `cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)`
2. **Otsu thresholding** — automatically finds the optimal foreground/background split; produces a clean binary image without a hardcoded threshold
3. **Canny edge detection** — extracts crisp edge lines (`threshold1=50`, `threshold2=150`)
4. **Overlay** — edges are merged onto the binary image with `cv2.bitwise_or`, giving solid regions + sharp outlines

---

## ⚡ VRAM Optimisations

The model is loaded with three optimisations for 4 GB GPUs:

| Optimisation | Method | Effect |
|---|---|---|
| Attention slicing | `pipe.enable_attention_slicing()` | Processes attention heads in chunks |
| VAE slicing | `pipe.vae.enable_slicing()` | Decodes latents one image at a time |
| CPU offloading | `pipe.enable_model_cpu_offload()` | Moves sub-models to CPU when idle |

Images are generated **one at a time** (not batched), keeping peak VRAM flat regardless of `num_images`.

---

## 🎯 Prompt Guidelines

The prompt should describe the **subject only** — the template handles style and format.

### ✅ Good prompts

```
a camera
a coffee cup
a lightning bolt
a wifi signal
a dragon head, side profile, simple silhouette
a camera, front view, lens in center
```

### ❌ Avoid

```
dragon                    # too vague
a beautiful illustration  # wrong style framing
generate an icon of X     # instruction framing confuses SD
```

---

## 📦 Dependencies

```
fastapi
uvicorn[standard]
torch                       # install with CUDA wheel separately
diffusers
transformers
accelerate
safetensors
Pillow
opencv-python-headless
numpy
```
---

# 📦 Pull from GitHub Container Registry

The Docker image for this project is available via GitHub Container Registry.

#### 🔗 Image

```
ghcr.io/adityakarippadathudai/icon-generator:latest
```

#### 📥 Pull the image

```bash
docker pull ghcr.io/adityakarippadathudai/icon-generator:latest
```

#### ▶️ Run the container

```bash
docker run -p 8000:8000 ghcr.io/adityakarippadathudai/icon-generator:latest
```

---

### ⚠️ Note

* The image size is large (~9 GB) due to included model weights.
* Initial pull may take significant time depending on your internet speed.

---

## ⚠️ Known Limitations

- Stable Diffusion 1.5 is not fine-tuned on icon datasets — outputs can be inconsistent
- Post-processing may over-threshold complex or detailed subjects
- Not suitable for production-quality SVG icons without further processing
- Generation takes ~10–30 seconds per image on a 4 GB GPU

---


## 🧠 What This Project Demonstrates

- End-to-end diffusion model integration with Hugging Face `diffusers`
- GPU memory optimisation for consumer hardware
- Prompt engineering for constrained image domains
- Pydantic schema validation in a FastAPI service
- Vanilla JS `fetch` API and dynamic DOM rendering
- Docker-based deployment with NVIDIA GPU passthrough

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📜 License

MIT License

---

## 👤 Author

**Aditya K U**
- GitHub: [@ AdityaKarippadathUdai](https://github.com/AdityaKarippadathUdai)
- LinkedIn: [https://www.linkedin.com/in/aditya-udai-a580a232a/](https://www.linkedin.com/in/aditya-udai-a580a232a/)

---

⭐ If this project was useful, give it a star on GitHub!