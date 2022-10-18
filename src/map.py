from osgeo import gdal,osr
import numpy as np
import data_classes as dc
from PIL import Image, ImageDraw


raster=r'test-top-right.tif'
longitude = 9.874404 
latitude = 52.442347



class GeoTif:
    width:int
    height:int
    coordTransform:any 
    geo_transform_inv:any

    def __init__(self, path:str):
        src = gdal.Open(path)

        self.width = src.RasterXSize
        self.height = src.RasterYSize

        point_srs = osr.SpatialReference()
        point_srs.ImportFromEPSG(4326) # hardcode for lon/lat
        point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)    

        file_srs = osr.SpatialReference()
        file_srs.ImportFromWkt(src.GetProjection())

        self.coordTransform = osr.CoordinateTransformation(point_srs, file_srs)
        self.geo_transform_inv = gdal.InvGeoTransform(src.GetGeoTransform())

        del src

    def toPixelCoord(self, lat:float, lon:float) -> tuple[int, int]:
        '''Takes latitude and longitude and returns corresponding (x,y) as pixel in the image'''
        point_x = lon
        point_y = lat
        mapx, mapy, _ = self.coordTransform.TransformPoint(point_x, point_y)

        pixel_x, pixel_y = gdal.ApplyGeoTransform(self.geo_transform_inv, mapx, mapy)

        # round to pixel
        pixel_x = round(pixel_x)
        pixel_y = round(pixel_y)

        return pixel_x, pixel_y


a = GeoTif(raster)
og = a.toPixelCoord(latitude, longitude)
print(og)

off = a.toPixelCoord(52.456301, 9.885560)
print(off)

tr = a.toPixelCoord(52.454889, 9.882972)
print(tr)
bl = a.toPixelCoord(52.437119, 9.853202)
print(bl)

im = Image.new('L', (10_000, 10_000))
draw = ImageDraw.Draw(im)
draw.line((off, og, bl ), fill=255, width=10)
im.show()
