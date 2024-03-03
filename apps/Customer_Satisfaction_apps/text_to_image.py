import io
import os
from PIL import Image
from io import BytesIO
import base64
import requests, json

hf_api_key = "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"

def get_completion(inputs, parameters=None, ENDPOINT_URL='https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5'):
    headers = {
      "Authorization": f"Bearer {hf_api_key}",
      "Content-Type": "application/json"
    }   
    data = { "inputs": inputs }
    if parameters is not None:
        data.update({"parameters": parameters})
    response = requests.request("POST",
                                ENDPOINT_URL,
                                headers=headers,
                                data=json.dumps(data))
    print("response.status_code", response.status_code)
    print(response.headers.get ('content-type'))
    print("---------------------------------")
    try:
        content = response.content
        print(type(content))
        return content

    except json.JSONDecodeError as e:
        print(f"Error: JSONDecodeError - {e}")
        print("Response Content:", content)
        return None

def base64_to_pil(img_base64):
    #base64_decoded = base64.b64decode(img_base64)
    byte_stream = io.BytesIO(img_base64)
    pil_image = Image.open(byte_stream)
    return pil_image

def generate(prompt, negative_prompt, steps, guidance, width, height):
    params = {
        "negative_prompt": negative_prompt,
        "num_inference_steps": steps,
        "guidance_scale": guidance,
        "width": width,
        "height": height
    }
    
    output = get_completion(prompt, params)
    pil_image = base64_to_pil(output)
    return pil_image

