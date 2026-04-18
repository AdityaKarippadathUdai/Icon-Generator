import base64
from io import BytesIO
from typing import List, Optional

import torch
from diffusers import StableDiffusionPipeline

from config import (
    BASE_PROMPT_TEMPLATE,
    IMAGE_SIZE,
    MODEL_PATH,
    NEGATIVE_PROMPT,
    STYLE_PRESETS,
)

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def _load_pipeline() -> StableDiffusionPipeline:
    pipe = StableDiffusionPipeline.from_single_file(
        MODEL_PATH,
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.to("cuda")

    # Low-VRAM optimisations
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    pipe.enable_model_cpu_offload()

    return pipe


# Load once at import time so the model stays warm across requests.
_pipe: StableDiffusionPipeline = _load_pipeline()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_icon(
    prompt: str,
    style: str,
    num_images: int,
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
    style_desc = STYLE_PRESETS.get(style, STYLE_PRESETS["minimal"])
    full_prompt = BASE_PROMPT_TEMPLATE.format(object=prompt, style=style_desc)

    generator = (
        torch.Generator(device="cuda").manual_seed(seed)
        if seed is not None
        else None
    )

    images_b64: List[str] = []

    for i in range(num_images):
        # Use a unique seed per image when a base seed is supplied so that
        # multiple results are distinct but still reproducible.
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