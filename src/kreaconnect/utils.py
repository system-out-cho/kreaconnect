import requests
import torch
import requests
import os
import time
import numpy as np
from PIL import Image
import io
from dotenv import load_dotenv

api_key = ""

# max_time for generation to run before time out
max_time = 120

# load dotenv
load_dotenv()

# function that sets the API key from env
def setKey():
    global api_key
    api_key = os.getenv("KREA_API_KEY")
    return api_key

# test function that sends request for all jobs
def sendRequest():
    # url = "https://api.krea.ai/jobs?limit=100&status=queued"
    url = "https://api.krea.ai/jobs?limit=100"
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(url, headers=headers)
    print("PRINTING response.text from sendrequest!!!")
    print(response.text)

# converts an image tensor into bytes
def tensor_to_bytes(image_tensor):
    # Take first image from batch, convert to uint8
    img_np = (image_tensor[0].numpy() * 255).astype(np.uint8)
    pil_image = Image.fromarray(img_np)
    
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    print(buf)
    return buf

# converts url to tensor 
def url_to_tensor(image_url):
    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Convert to PIL, then numpy, then tensor
    pil_image = Image.open(io.BytesIO(response.content)).convert("RGB")
    img_np = np.array(pil_image).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img_np).unsqueeze(0)  # add batch dimension
    
    return tensor

# function that takes in job_id and checks if it is completed every 2s
# times out after max_time
# returns the result url if completed
def checkJob(job_id):
    print("beginning of check job function")
    start_time = time.time()
    timeout = max_time  # 1 minute
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
        
        #runs every 2 seconds
        time.sleep(2)

# uploads image asset to Krea to be used for generation
def upload_to_krea(image):    
    img_bytes = tensor_to_bytes(image)

    url = "https://api.krea.ai/assets"

    files = { "file": ("input_image.png", img_bytes, "image/png") }
    payload = { "description": "<string>" }
    headers = {"Authorization": "Bearer " + api_key}

    response = requests.post(url, data=payload, files=files, headers=headers)

    return response.json()["image_url"]

def upload_img_arr_krea(image_arr):
    img_url_arr = []

    for img in image_arr:
        if img != None:
            img_url = upload_to_krea(img)
            img_url_arr.append(img_url)
    
    return img_url_arr

def sendJob(url, payload, headers):
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        data = response.json()
        job_id = data["job_id"]
        return checkJob(job_id)