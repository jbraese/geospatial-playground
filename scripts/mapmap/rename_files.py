import os
import shutil

data_folder = "./data/raw/"
out_folder = "./data/renamed/"

images = []
for file in os.listdir(data_folder):
    file_parts = file.split("~")
    if len(file_parts)>1:
        images.append(file_parts[0])
        
for i, image in enumerate(images):
    shutil.copyfile(os.path.join(data_folder, image + ".jpg"), os.path.join(out_folder, f"map_{i:02}_full.jpg"))
    shutil.copyfile(os.path.join(data_folder, image + "~2.jpg"), os.path.join(out_folder, f"map_{i:02}_coverage.jpg"))
    
print(f"copied and renamed {i} files")
            
    