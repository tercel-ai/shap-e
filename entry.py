import os
import io
import time
import torch
import json
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget
from shap_e.util.notebooks import decode_latent_mesh


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
xm = load_model('transmitter', device=device)
model = load_model('text300M', device=device)
diffusion = diffusion_from_config(load_config('diffusion'))

expire_time = int(os.environ.get('SHAPE_FILE_EXPIRE_TIME', 900))
max_files = int(os.environ.get('SHAPE_FILE_MAX', 100))
rate_limit = int(os.environ.get('SHAPE_FILE_RATE_LIMIT', 1))

last_create_time = time.time()
run_count = 0
dir_path = 'statics'

class RateLimitExcepiton(Exception):
    pass

def save_image(images, filename):
    writer = io.BytesIO()
    images[0].save(
        writer, format="GIF", save_all=True, append_images=images[1:], duration=100, loop=0
    )
    writer.seek(0)
    with open(f'{dir_path}/{filename}.gif', "wb") as f:
        f.write(writer.read())


def text_to_3d(prompt:str, filename:str, batch_size=1, guidance_scale=15.0):
    global last_create_time
    global run_count

    run_count += 1

    try:
        last_create_time = time.time()

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

        render_mode = 'nerf'  # you can change this to 'stf'
        size = 600  # this is the size of the renders; higher values take longer to render.

        cameras = create_pan_cameras(size, device)
        for i, latent in enumerate(latents):
            images = decode_latent_images(xm, latent, cameras, rendering_mode=render_mode)
            save_image(images, filename)


        for i, latent in enumerate(latents):
            with open(f'{dir_path}/{filename}.{i}.ply', 'wb') as f:
                decode_latent_mesh(xm, latent).tri_mesh().write_ply(f)
    
    except Exception as e:
        print('generate 3d exception: '+str(e))

    finally:
        run_count -= 1


def can_create():
    clear_files()
    if run_count >= rate_limit:
        return False

    return True

def clear_files():
    count = 0
    file_list = get_files()
    total = len(file_list)
    for i in range(total):
        if time.time()-file_list[i]['create_time'] > expire_time:
            file_path = os.path.join(dir_path, file_list[i]['filename'])
            res = delete_file(file_path)
            if res:
                count += 1
          
    total = len(file_list)
    if total > max_files:
        file_list = file_list[:10]
        total = len(file_list)
        for i in range(total): 
            file_path = os.path.join(dir_path, file_list[i]['filename'])
            res = delete_file(file_path)
            if res:
                count += 1
    return count

def delete_file(filepath):
    try:
        os.remove(filepath)
        return True
    except OSError as e:
        print(f'can not delete {filepath}: {e.strerror}')
        return False

    
def get_files():
    data = []
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            create_time = os.path.getctime(file_path)
            data.append({
                'filename': file_name,
                'create_time': create_time
            })

    sorted_data = sorted(data, key=lambda x: x['create_time'])
    return sorted_data

def count_files():
    count = 0
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            count += 1

    return count
