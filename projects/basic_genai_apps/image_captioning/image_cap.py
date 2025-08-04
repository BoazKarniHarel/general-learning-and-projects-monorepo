from PIL import Image

import requests
from transformers import AutoProcessor, BlipForConditionalGeneration

# Load the pretrained processor and model
processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base") 
"""This is a processor class that is used for preprocessing data for the BLIP model. 
It wraps a BLIP image processor and an OPT/T5 tokenizer into a single processor. 
This means it can handle both image and text data, preparing it for input into the BLIP model."""
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
"""This is a model class that is used for conditional text generation given an image and an optional text prompt. 
In other words, it can generate text based on an input image and an optional piece of text. 
This makes it useful for tasks like image captioning or visual question answering, 
where the model needs to generate text that describes an image or answer a question about an image."""

img_path = r"C:\Users\boazk\Downloads\random_phots\IMG_2238.JPG"
# convert it into an RGB format 
image = Image.open(img_path).convert('RGB')

text = "the image of"
inputs = processor(images=image, text=text, return_tensors="pt")

outputs = model.generate(**inputs, max_length=50)

caption = processor.decode(outputs[0], skip_special_tokens=True)

print(caption)
