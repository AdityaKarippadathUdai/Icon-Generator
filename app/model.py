import base64
from io import BytesIO
from typing import List, Optional

import torch
from diffusers import StableDiffusionPipeline

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_PATH    = "/home/aditya/Project/icon_generator/models/v1-5-pruned-emaonly.safetensors"
IMAGE_SIZE    = 512
NEGATIVE_PROMPT = "realistic, photo, 3d, shadows, messy, text"

PROMPT_TEMPLATE = (
    "A clean minimalist flat icon of {prompt}, "
    "vector style, black outline, white background"
)

STYLE_PRESETS = {
    "minimal": "minimal linework, clean outlines, simple shapes, monochrome",
    "filled":  "bold filled shapes, flat colors, solid design, no outlines",
    "neon":    "neon glowing colors, dark background, vibrant electric hues, luminous edges",
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
    pipe.to("cuda")

    # Low-VRAM optimisations
    pipe.enable_attention_slicing()
    pipe.vae.enable_slicing()          # replaces deprecated enable_vae_slicing()
    pipe.enable_model_cpu_offload()

    return pipe


# Load once at import time so the model stays warm across requests.
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
    """
    Generate icon images and return them as base64-encoded PNG strings.

    Args:
        prompt:     Object / subject description (e.g. "a camera").
        style:      Key into STYLE_PRESETS ("minimal", "filled", "neon").
        num_images: Number of images to generate (1–4).
        seed:       Optional RNG seed for reproducibility.

    Returns:
        List of base64-encoded PNG strings, one per image.
    """
    style_desc  = STYLE_PRESETS.get(style, STYLE_PRESETS["minimal"])
    full_prompt = PROMPT_TEMPLATE.format(prompt=prompt) + f", {style_desc}"

    generator = (
        torch.Generator(device="cuda").manual_seed(seed)
        if seed is not None
        else None
    )

    images_b64: List[str] = []

    for i in range(num_images):
        # Offset seed per image so multiple results are distinct but reproducible.
        if generator is not None and num_images > 1:
            generator.manual_seed(seed + i)

        result = _pipe(
            prompt=full_prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=IMAGE_SIZE,
            height=IMAGE_SIZE,
            num_inference_steps=30,
            guidance_scale=7.5,
            generator=generator,
            num_images_per_prompt=1,
        )

        image = result.images[0]

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        images_b64.append(base64.b64encode(buffer.read()).decode("utf-8"))

    return images_b64