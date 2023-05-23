import time
import torch
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
# from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget
from shap_e.util.notebooks import decode_latent_mesh


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
xm = load_model('transmitter', device=device)
model = load_model('text300M', device=device)
diffusion = diffusion_from_config(load_config('diffusion'))

max_files = 3
file_list = []
busy_wait_time = 180
last_create_time = time.time()

class RateLimitExcepiton(Exception):
    pass


def generate_ply(prompt:str, filename:str, batch_size=1, guidance_scale=15.0):
    try:
        latents = sample_latents(
            batch_size=batch_size,
            model=model,
            diffusion=diffusion,
            guidance_scale=guidance_scale,
            model_kwargs=dict(texts=[prompt] * batch_size),
            progress=True,
            clip_denoised=True,
            use_fp16=True,
            use_karras=True,
            karras_steps=64,
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0,
        )

        # render_mode = 'nerf'  # you can change this to 'stf'
        # size = 64  # this is the size of the renders; higher values take longer to render.

        # cameras = create_pan_cameras(size, device)
        # for i, latent in enumerate(latents):
        #     images = decode_latent_images(xm, latent, cameras, rendering_mode=render_mode)
            # display(gif_widget(images))


        for i, latent in enumerate(latents):
            with open(f'statics/{filename}.{i}.ply', 'wb') as f:
                decode_latent_mesh(xm, latent).tri_mesh().write_ply(f)
    
    except Exception as e:
        pass


async def create_3d(prompt:str, filename:str, batch_size=1, guidance_scale=15.0):
    if len(file_list) >= max_files:
        return
    
    last_create_time = time.time()
    file_list.append(filename)
    generate_ply(prompt, filename)


def can_create():
    if time.time() - last_create_time > busy_wait_time:
        # todo delete first file
        pass

    return len(file_list) < max_files