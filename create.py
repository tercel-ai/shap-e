import os
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

expire_time = 900
max_files = 100
file_list = []
last_create_time = time.time()
rate_limit = 1
run_count = 0

class RateLimitExcepiton(Exception):
    pass


def generate_ply(prompt:str, filename:str, batch_size=1, guidance_scale=15.0):
    global last_create_time
    global run_count

    run_count += 1
    last_create_time = time.time()

    for i in range(batch_size):
        file_list.append({'filename': f'statics/{filename}.{i}.ply', 'time': time.time()})

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
        del file_list[-1*batch_size:]

    finally:
        run_count -= 1


async def create_3d(prompt:str, filename:str, batch_size=1, guidance_scale=15.0):
    if run_count >= rate_limit:
        return False
    
    generate_ply(prompt, filename)
    return True


def can_create():
    clear_files()
    if run_count >= rate_limit:
        return False

    return True

def clear_files():
    count = len(file_list)
    for i in range(count):
        if time.time()-file_list[i]['time'] > expire_time:
            delete_file(file_list[i]['filename'])
            del file_list[i]
                
    count = len(file_list)
    if count > max_files:
        for i in range(10): 
            delete_file(file_list[i]['filename'])
            del file_list[i]

def delete_file(filepath):
    try:
        os.remove(filepath)
    except OSError as e:
        print(f'can not delete {filepath}: {e.strerror}')

    
def show_files():
    data = []
    dir_path = 'statics'

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            create_time = os.path.getctime(file_path)
            # 将时间戳转换为可读格式
            readable_time = time.ctime(create_time)

            data.append({
                'filename': file_name,
                'create_time': create_time,
                'readable_time': readable_time
            })

    return data