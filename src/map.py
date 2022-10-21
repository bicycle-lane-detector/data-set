from sklearn.linear_model import orthogonal_mp
from osgeo import gdal,osr
import numpy as np
import data_classes as dc
from PIL import Image, ImageDraw
import os
from tqdm import tqdm
import glob
from typing import Union

'''
cycling lane width:13px, 13px, 12 px, 10px, 9.5px, 10.5 px, 13 px, 10px, 13px, 14px, 11px, 11 px, 14px, 14 px, 11px, 10px ~ avg 11.8125
car lane width: 15 px, 18px, 17px, 21px, 17px, 15, 17, 16px, 13 px, 23px, 16px, 17px, 22px, 22px, 18px, 15px ~ avg 17.625
but beware tram tracks
'''

DISTANCE_FROM_CENTER_LINE_PER_CAR_LANE = 17.625
MASK_LINE_WIDTH = 11.8125

IMG_WIDTH = IMG_HEIGHT = 10_000

class GeoTif:
    width:int
    height:int
    name:str
    _coordTransform:any 
    _geo_transform_inv:any

    def __init__(self, path:str):
        self.name = os.path.basename(path)

        src = gdal.Open(path)

        self.width = src.RasterXSize
        self.height = src.RasterYSize

        point_srs = osr.SpatialReference()
        point_srs.ImportFromEPSG(4326) # hardcode for lon/lat
        point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)    

        file_srs = osr.SpatialReference()
        file_srs.ImportFromWkt(src.GetProjection())

        self._coordTransform = osr.CoordinateTransformation(point_srs, file_srs)
        self._geo_transform_inv = gdal.InvGeoTransform(src.GetGeoTransform())

        del src

    def toPixelCoord(self, lat:float, lon:float) -> tuple[int, int]:
        '''Takes latitude and longitude and returns corresponding (x,y) as pixel in the image'''
        point_x = lon
        point_y = lat
        mapx, mapy, _ = self._coordTransform.TransformPoint(point_x, point_y)

        pixel_x, pixel_y = gdal.ApplyGeoTransform(self._geo_transform_inv, mapx, mapy)

        # round to pixel
        pixel_x = round(pixel_x)
        pixel_y = round(pixel_y)

        return pixel_x, pixel_y


def extractLanes(street: dc.Street, v_list:list) -> tuple[list, list]:
    left_track = []
    right_track = []
    
    for i in range(len(v_list) - 1):
        start = v_list[i]
        start = np.array(start)
        end = v_list[i+1]
        end = np.array(end)

        v = end - start
        v_x, v_y = v
        orthogonal_left = np.array([v_y, -v_x]) # vector turned by 90° clockwise in "upside-down" 2D
        orthogonal_left = orthogonal_left / np.sqrt(np.sum(orthogonal_left**2)) # make unit vector
        orthogonal_left *= street.n_car_lanes / 2 * DISTANCE_FROM_CENTER_LINE_PER_CAR_LANE 
        + MASK_LINE_WIDTH / 2 # extend to desired length

        orthogonal_right = -orthogonal_left # vector turned by 90° counter-clockwise in "upside-down" 2D and extended to deisred length

        if street.bike_left:
            left_track.extend([tuple(start + orthogonal_left), tuple(end + orthogonal_left)])
        if street.bike_right:
            right_track.extend([tuple(start + orthogonal_right), tuple(end + orthogonal_right)])

    return left_track, right_track

def draw(canvas:ImageDraw.ImageDraw, road:Union[dc.CycleWay,dc.Street], vectors:list[tuple[int, int]]) -> None:
    width = round(MASK_LINE_WIDTH)
    if type(road) is dc.CycleWay:
        canvas.line(vectors, fill=road.MASK_VALUE, width=width)
    if type(road) is dc.Street:
        left, right = extractLanes(road, vectors)
        canvas.line(left, fill=road.MASK_VALUE, width=width)
        canvas.line(right, fill=road.MASK_VALUE, width=width)


if __name__ == "__main__":
    path = "D:\Studienarbeit\hannover_alle"

    path_to_tifs = os.path.join(path, "*.tif")
    tifs = [GeoTif(fname) for fname in glob.glob(path_to_tifs)]

    print("Found", len(tifs), "GeoTifs.")

    # load OSM data 
    osm_data = [dc.Street([dc.Node(52.456301, 9.885560), dc.Node(52.442347, 9.874404), dc.Node(52.437119, 9.853202)], 6, True, True), 
    dc.CycleWay([dc.Node(52.456301, 9.885560), dc.Node(52.442347, 9.874404), dc.Node(52.437119, 9.853202)])]
    print("Loaded", len(osm_data), "individual road segments with, in total,", sum(len(i.nodes) for i in osm_data),"data points.")

    print("Creating masks by applying road segments...")
    for tif in tqdm(tifs, total=len(tifs)):
        mask = Image.new('L', (IMG_WIDTH, IMG_HEIGHT))
        canvas = ImageDraw.Draw(mask)

        for road in osm_data:
            vectors = [tif.toPixelCoord(node.lat, node.lon) for node in road.nodes]
            draw(canvas, road, vectors)

        mask.save(os.path.join(path, tif.name[:-3] + "png"))
        
        

'''
raster=r'test-top-right.tif'
longitude = 9.874404 
latitude = 52.442347

a = GeoTif(raster)
og = a.toPixelCoord(latitude, longitude)
print(og)

off = a.toPixelCoord(52.456301, 9.885560)
print(off)

tr = a.toPixelCoord(52.454889, 9.882972)
print(tr)
bl = a.toPixelCoord(52.437119, 9.853202)
print(bl)

'''
