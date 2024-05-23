from datetime import datetime
import urllib.request
import base64
import json
import time
import os

webui_server_url = 'http://35.201.202.64:7860'

out_dir = 'api_out'
out_dir_t2i = os.path.join(out_dir, 'txt2img')
out_dir_i2i = os.path.join(out_dir, 'img2img')
os.makedirs(out_dir_t2i, exist_ok=True)
os.makedirs(out_dir_i2i, exist_ok=True)


def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def set_options(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))

def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def call_txt2img_api(**payload):
    response = call_api('sdapi/v1/txt2img', **payload)
    for index, image in enumerate(response.get('images')):
        return image
        # save_path = os.path.join(out_dir_t2i, f'txt2img-{timestamp()}-{index}.png')
        # decode_and_save_base64(image, save_path)


def call_img2img_api(**payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')):
        save_path = os.path.join(out_dir_i2i, f'img2img-{timestamp()}-{index}.png')
        decode_and_save_base64(image, save_path)


# if __name__ == '__main__':


    # options = {"sd_model_checkpoint":"AnythingXL_xl.safetensors [8421598e93]"}
    # set_options("sdapi/v1/options", **options)
    # payload = {
    #     "prompt": "masterpiece, best quality, colorful and vibrant, landscape, extremely detailed, cozy illustration, illustration, lofi, comforting to look at, a very detailed coffee shop from outside, with a big tree next to it, blue sky, road with pebbles on it, much much detailed, a night scene",  # extra networks also in prompts
    #     "negative_prompt": "explicit, sensitive, nsfw, low quality, worst quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
    #     "seed": 1,
    #     "steps": 20,
    #     "width": 52,
    #     "height": 52,
    #     "cfg_scale": 7,
    #     "sampler_name": "Euler a",
    #     "n_iter": 1,
    #     "batch_size": 1,
    # }
    # call_txt2img_api(**payload)