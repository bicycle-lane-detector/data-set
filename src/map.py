from sklearn.linear_model import orthogonal_mp
from osgeo import gdal,osr
import numpy as np
import data_classes as dc
from PIL import Image, ImageDraw

DISTANCE_FROM_CENTER_LINE_PER_CAR_LANE = 20

raster=r'test-top-right.tif'
longitude = 9.874404 
latitude = 52.442347



class GeoTif:
    width:int
    height:int
    _coordTransform:any 
    _geo_transform_inv:any

    def __init__(self, path:str):
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
        print("vecs")
        print(v)
        v_x, v_y = v
        orthogonal_left = np.array([v_y, -v_x]) # vector turned by 90° clockwise in "upside-down" 2D
        print(orthogonal_left)
        orthogonal_left = orthogonal_left / np.sqrt(np.sum(orthogonal_left**2)) # make unit vector
        orthogonal_left *= street.n_car_lanes / 2 * DISTANCE_FROM_CENTER_LINE_PER_CAR_LANE # extend to desired length

        orthogonal_right = -orthogonal_left # vector turned by 90° counter-clockwise in "upside-down" 2D and extended to deisred length

        if street.bike_left:
            left_track.extend([tuple(start + orthogonal_left), tuple(end + orthogonal_left)])
        if street.bike_right:
            right_track.extend([tuple(start + orthogonal_right), tuple(end + orthogonal_right)])

    return left_track, right_track


a = GeoTif(raster)
og = a.toPixelCoord(latitude, longitude)
print(og)

off = a.toPixelCoord(52.456301, 9.885560)
print(off)

tr = a.toPixelCoord(52.454889, 9.882972)
print(tr)
bl = a.toPixelCoord(52.437119, 9.853202)
print(bl)

path = (off, og, bl )
s = dc.Street([], 2, True, False)

left, right = extractLanes(s, path)

im = Image.new('L', (10_000, 10_000))
draw = ImageDraw.Draw(im)
draw.line(path, fill=100, width=10)

print(left)
draw.line(left, fill=255, width=10)
draw.line(right, fill=255, width=10)


im.show()
