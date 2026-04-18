MODEL_PATH = "/home/aditya/Project/icon_generator/models/v1-5-pruned-emaonly.safetensors"
IMAGE_SIZE = 512

NEGATIVE_PROMPT = "realistic, photo, 3d, shadows, gradients, messy, text, watermark"

STYLE_PRESETS = {
    "minimal": "minimal linework, clean outlines, simple shapes, monochrome",
    "filled": "bold filled shapes, flat colors, solid design, no outlines",
    "neon": "neon glowing colors, dark background, vibrant electric hues, luminous edges",
}

BASE_PROMPT_TEMPLATE = (
    "A clean minimalist flat icon of {object}, {style}, "
    "vector style, centered, white background, high contrast"
)