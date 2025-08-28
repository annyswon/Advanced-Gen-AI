# Art Capstone – Alternative Media Cover

## Objective
Design a new cover for an iconic media piece.  
The goal is to create an alternative variation of an existing cover using a **self-hosted AI image generation workflow** (ComfyUI with Stable Diffusion XL).  
No cloud-hosted or external services (like Sora/Replicate) were used — only a locally run pipeline.

## Original Work
![Original Vogue Cover](vogue_france_dec2024.jpg)

## AI-Generated Cover
![Generated Vogue Cover](generated_vogue_cover.png)

## Workflow

### Model
- **Model used:** Stable Diffusion XL Base 1.0  
- **File:** `sdxl_base_1.0.safetensors`  
- **Source:** [Stable Diffusion XL Base 1.0 – Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

### Technical Generation Details
- **Steps:** 36  
- **CFG Scale:** 7.8  
- **Sampler:** dpmpp_2m  
- **Scheduler:** karras  
- **Resolution:** 1024 × 1536  
- **Seed:** randomized  
- **Batch size:** 1  

### Prompt

**Positive prompt:**
high-fashion editorial magazine cover, elegant female model in white couture jacket with feather trim and pearls, bold red lipstick, studio photography, minimal white background, cinematic lighting, glossy magazine style, Parisian Vogue composition, sharp focus, professional retouching, full torso portrait

**Negative prompt:**
cartoon, anime, 3d, cgi, blurry, lowres, text, watermark, bad hands, extra limbs, distorted face, oversaturated, artifacts, logo

### Pipeline Screenshot
![ComfyUI Workflow](workflow_screenshot.png)

## Resources Used
- **Environment:** ComfyUI running locally on macOS  
- **System:** Apple MacBook Pro (M1 chip, 16 GB RAM, shared 16 GB VRAM)  
- **Frameworks:** Python 3.11, ComfyUI v0.3.53  
- **Model Source:** Hugging Face (Stable Diffusion XL Base 1.0)  
- **Output directory:** `~/ComfyUI/output/`

## Media Option
- Chosen type: **Magazine Cover**  
- Original: *Vogue France, December 2024 / January 2025*  
- Generated: Alternative Vogue-style cover with Stable Diffusion XL
