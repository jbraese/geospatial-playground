import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, Point, GeometryCollection
from shapely import intersection, difference 
from dataclasses import dataclass
from typing import List
import os

##################################################################
# this script takes a number of individual input polygons (as geojson feature 
# collection) and aggregates them into a polygon heatmap: a collection of new 
# spatially disjoint polygons where each polygon contains information on how many
# (and which) input polygons it is aggregated from. 
##################################################################


data_folder = "./mapmap/data/processed"
geojson_path = "map_coverages.json"


@dataclass
class HeatmapElement:
    """ A polygon in the heatmap that is covered by a number of maps"""
    shape: Polygon
    n_maps: int
    map_ids: List[int]
    
    def as_dict(self):
        return {'geometry': self.shape, 'n_maps': self.n_maps, 'map_ids': self.map_ids}


def get_heatmap_elems(shape, n_maps:int, map_ids: List[int]) -> List[HeatmapElement]:
    """ get an individual HatmapElement for each polygon in 
     <shape> (which could be any shapely geometry type)"""
    if shape.is_empty:
        return []
    elif type(shape) == Polygon:
        return [HeatmapElement(shape, n_maps, map_ids)]
    elif type(shape) == MultiPolygon:
        return [HeatmapElement(geom, n_maps, map_ids) for geom in shape.geoms]
    elif type(shape) == Point:
        return []
    elif type(shape) == GeometryCollection:
        return [HeatmapElement(geom, n_maps, map_ids) for geom in shape.geoms 
                if type(geom) == Polygon]
    else:
        raise NotImplementedError()


in_path = os.path.join(data_folder, geojson_path)

print("Reading file from", in_path)
gdf = gpd.read_file(in_path, driver='GeoJSON')
assert all([type(geom) == Polygon for geom in gdf.geometry]), \
    "Input geojson should contain only Polygons"

print(f"Aggregating {len(gdf)} individual polygons into a polygon heatmap... ")
heatmap_elems = []
for _, row in gdf.iterrows():
    new_heatmap_elems = []
    new_map_id = row.map_id
    new_shape = row.geometry
    print("processing polygon with id:", new_map_id)
    for old_elem in heatmap_elems:
        if not new_shape.intersects(old_elem.shape):
            new_heatmap_elems.append(old_elem)
        else:
            intersecting_ids = old_elem.map_ids + [new_map_id]
            print("intersection with ids:", intersecting_ids)

            # first we add the intersecting part, noting its increased coverage
            intersecting_shape = intersection(new_shape, old_elem.shape)
            intersecting_elems = get_heatmap_elems(
                intersecting_shape, old_elem.n_maps + 1, intersecting_ids)
            new_heatmap_elems.extend(intersecting_elems)                

            # the non-intersecting parts of old elem we add back to the list
            only_old_shape = difference(old_elem.shape, new_shape)
            only_old_elems = get_heatmap_elems(
                only_old_shape, old_elem.n_maps, old_elem.map_ids)
            new_heatmap_elems.extend(only_old_elems)  

            # finally we remove the intersecting parts from new shape
            # this we append only outside the inner loop,
            # because it might intersect with other old elems still
            new_shape = difference(new_shape, old_elem.shape)

    # add remaining new_shape that intersects with nothing to the elems
    new_elems = get_heatmap_elems(new_shape, 1, [new_map_id])
    new_heatmap_elems.extend(new_elems)
    heatmap_elems = new_heatmap_elems

print("\nFinished processing. \nResulting amount of heatmap polygons: ", len(heatmap_elems))
gdf = gpd.GeoDataFrame([x.as_dict() for x in heatmap_elems], crs='epsg:4326')
gdf["map_ids"] = gdf["map_ids"].astype(str)
out_path = os.path.join(data_folder, "poly_heatmap.json")
gdf.to_file(out_path, driver="GeoJSON") 
print("wrote resulting polygon heatmap to", out_path)
