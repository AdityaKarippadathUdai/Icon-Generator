import torch
from diffusers import StableDiffusionPipeline
from io import BytesIO
import base64

MODEL_PATH = "models/v1-5-pruned-emaonly.safetensors"

pipe = StableDiffusionPipeline.from_single_file(
    MODEL_PATH,
    torch_dtype=torch.float16
).to("cuda")

pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
pipe.enable_model_cpu_offload()

def generate_icon(prompt, num_images=1):
    results = []

    full_prompt = f"A clean minimalist flat icon of {prompt}, vector style, black outline, white background"
    negative_prompt = "realistic, photo, 3d, shadows, messy, text"

    for _ in range(num_images):
        image = pipe(
            full_prompt,
            negative_prompt=negative_prompt,
            height=512,
            width=512
        ).images[0]

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        results.append(img_str)

    return results