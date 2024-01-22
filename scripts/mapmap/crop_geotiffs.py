import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.crs import CRS

in_folder = "./data/renamed/"
out_folder = "./data/processed/"

tifs = [f for f in os.listdir(in_folder) if f.endswith("_modified.tif")]
shapes = gpd.read_file(os.path.join(out_folder, "map_coverages.gpkg"))
shapes = shapes.to_crs(epsg=3857)   

for tif in tifs:
    map_id = int(tif.split("_")[1])
    # crop raster to shape and write cropped tif
    shape = shapes.loc[shapes.map_id==map_id, "geometry"].iloc[0]
    
    crs = CRS.from_epsg(3857)
    with rasterio.open(os.path.join(in_folder, tif), "r+") as src:
        out_image, out_transform = mask(src, [shape], crop=True, nodata=255)
        src.crs = crs
        out_meta = src.profile
    out_meta.update({"height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    
    out_tif = os.path.join(out_folder, f"map_{map_id:02}.tif")
    with rasterio.open(out_tif, "w", **out_meta) as dest:
        dest.write(out_image)
    print("wrote", out_tif)

shapes.to_crs(epsg=4326).to_file(os.path.join(out_folder, "map_coverages.json"), driver="GeoJSON") 
