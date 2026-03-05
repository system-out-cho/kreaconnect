import requests
import torch
import requests
import os
import time
import numpy as np
from PIL import Image
import io

api_key = ""

def setKey():
    global api_key
    api_key = os.getenv("KREA_API_KEY")
    return api_key

def sendRequest():
    # url = "https://api.krea.ai/jobs?limit=100&status=queued"
    url = "https://api.krea.ai/jobs?limit=100"
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(url, headers=headers)
    print("PRINTING response.text from sendrequest!!!")
    print(response.text)

def tensor_to_bytes(image_tensor):
    # Take first image from batch, convert to uint8
    img_np = (image_tensor[0].numpy() * 255).astype(np.uint8)
    pil_image = Image.fromarray(img_np)
    
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    print(buf)
    return buf

def tensor_to_bytes(image_tensor):
    # Take first image from batch, convert to uint8
    img_np = (image_tensor[0].numpy() * 255).astype(np.uint8)
    pil_image = Image.fromarray(img_np)
    
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    print(buf)
    return buf

def url_to_tensor(image_url):
    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Convert to PIL, then numpy, then tensor
    pil_image = Image.open(io.BytesIO(response.content)).convert("RGB")
    img_np = np.array(pil_image).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img_np).unsqueeze(0)  # add batch dimension
    
    return tensor

def checkJob(job_id):
    print("beginning of check job function")
    start_time = time.time()
    timeout = 60  # 1 minute
    headers = {"Authorization": "Bearer " + api_key}
    url = f"https://api.krea.ai/jobs/{job_id}"

    while True:
        print("still checking job")

        if time.time() - start_time >= timeout:
            raise TimeoutError("Krea job timed out")

        response = requests.get(url, headers=headers)

        data = response.json()
        status = data["status"]

        if status == "completed":
            print("JOB COMPLETED!!")
            print(response.text)
            print("printing data")
            print(data)
            return data["result"]["urls"][0]
            # break
        
        #runs every 2 seconds
        time.sleep(2)

def upload_to_krea(image):    
    img_bytes = tensor_to_bytes(image)

    url = "https://api.krea.ai/assets"

    files = { "file": ("input_image.png", img_bytes, "image/png") }
    payload = { "description": "<string>" }
    headers = {"Authorization": "Bearer " + api_key}

    response = requests.post(url, data=payload, files=files, headers=headers)

    return response.json()["image_url"]