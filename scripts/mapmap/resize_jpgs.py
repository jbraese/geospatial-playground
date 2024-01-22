import os
from PIL import Image

in_folder = "./data/renamed/"
out_folder = "./data/final/"
jpgs = [f for f in os.listdir(in_folder) if f.endswith("_full.jpg")]

print(jpgs)
for jpg in jpgs:
    base_width= 800
    img = Image.open(os.path.join(in_folder, jpg))
    wpercent = (base_width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
    img.save(os.path.join(out_folder, jpg))
