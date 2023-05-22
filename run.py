import argparse
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
            with open(f'files/{filename}.{i}.ply', 'wb') as f:
                decode_latent_mesh(xm, latent).tri_mesh().write_ply(f)
    
    except Exception as e:
        pass



parser = argparse.ArgumentParser(description='Generate 3D')
parser.add_argument('--prompt', type=str, help='prompt word')
parser.add_argument('--filename', type=str, help='file name', default='exmaple')
parser.add_argument('--number', type=str, help='3d file numbers', default=1)
parser.add_argument('--scale', type=str, help='guidance scale', default=15.0)

args = parser.parse_args()


if __name__ == '__main__':
    generate_ply(args.prompt, args.filename, args.number, args.scale)
