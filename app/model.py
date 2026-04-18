import base64
from io import BytesIO
from typing import List, Optional

import torch
from diffusers import StableDiffusionPipeline

# ---------------------------------------------------------------------------
# Torch stability settings (IMPORTANT)
# ---------------------------------------------------------------------------

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.benchmark = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_PATH = "/home/aditya/Project/icon_generator/models/dreamshaper_8.safetensors"

IMAGE_SIZE = 256  # keep low for 4GB VRAM

NEGATIVE_PROMPT = "realistic, photo, 3d, shadows, messy, text, watermark"

PROMPT_TEMPLATE = (
    "A clear simple icon of {prompt}, "
    "front view, centered, recognizable shape, "
    "designed as a UI icon, minimal design"
)
STYLE_PRESETS = {
    "minimal": (
        "simple flat icon, clean vector design, centered composition, "
        "clear recognizable object, thick black outline, minimal details, "
        "high contrast, white background, no shading, no gradients, "
        "symmetrical, icon style, UI icon"
    ),

    "filled": (
        "solid flat icon, bold filled shapes, clear silhouette, "
        "centered composition, minimal detail, high contrast colors, "
        "no gradients, no shadows, modern app icon style"
    ),

    "neon": (
        "neon glowing icon, dark background, bright glowing edges, "
        "cyberpunk style, high contrast, simple shape, centered icon, "
        "luminous outline, minimal detail"
    ),
}

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def _load_pipeline() -> StableDiffusionPipeline:
    pipe = StableDiffusionPipeline.from_single_file(
        MODEL_PATH,
        torch_dtype=torch.float16,
        use_safetensors=True,
        local_files_only=True,
    )

    # ✅ DO NOT use .to("cuda")

    # ✅ Stable low-VRAM config
    pipe.enable_attention_slicing()
    pipe.vae.enable_slicing()

    # 🔥 IMPORTANT: more stable than model_cpu_offload
    pipe.enable_sequential_cpu_offload()

    return pipe


# Load once globally
_pipe: StableDiffusionPipeline = _load_pipeline()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_icon(
    prompt: str,
    style: str = "minimal",
    num_images: int = 1,
    seed: Optional[int] = None,
) -> List[str]:

    style_desc = STYLE_PRESETS.get(style, STYLE_PRESETS["minimal"])
    full_prompt = PROMPT_TEMPLATE.format(prompt=prompt) + f", {style_desc}"

    images_b64: List[str] = []

    # ✅ CPU generator (prevents device mismatch)
    generator = None
    if seed is not None:
        generator = torch.Generator().manual_seed(seed)

    for i in range(num_images):

        if generator is not None and num_images > 1:
            generator.manual_seed(seed + i)

        try:
            result = _pipe(
                prompt=full_prompt,
                negative_prompt=NEGATIVE_PROMPT,
                width=IMAGE_SIZE,
                height=IMAGE_SIZE,
                num_inference_steps=60,   # 🔥 reduced → prevents crashes
                guidance_scale=7.5,       # 🔥 slightly lower = more stable
                generator=generator,
                num_images_per_prompt=1,
            )

            image = result.images[0]

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            images_b64.append(
                base64.b64encode(buffer.read()).decode("utf-8")
            )

            # 🔥 VERY IMPORTANT: prevent memory fragmentation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            print("Generation error:", e)
            continue

    return images_b64