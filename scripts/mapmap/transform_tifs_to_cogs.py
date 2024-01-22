import os
from osgeo import gdal

in_folder = "./data/renamed/"
out_folder = "./data/final/"

tifs = [f for f in os.listdir(in_folder) if f.endswith("_modified.tif")]

print(tifs)
for tif in tifs:
    map_id = int(tif.split("_")[1])
    out_tif = os.path.join(out_folder, f"map_{map_id:02}.tif")
    out_cog = out_tif[0:-4] + ".tif"
    map_id = int(tif.split("_")[1])
    ds = gdal.Open(os.path.join(in_folder, tif))
    gdal.SetConfigOption("COMPRESS_OVERVIEW", "DEFLATE")
    ds.BuildOverviews("NEAREST", [2,4])
    driver = gdal.GetDriverByName('GTiff')
    ds2 = driver.CreateCopy(out_cog, ds, options=["COPY_SRC_OVERVIEWS=YES" ,"TILED=YES", "COMPRESS=JPEG"])
    ds = None
    ds2 = None
    print("wrote", out_cog)
