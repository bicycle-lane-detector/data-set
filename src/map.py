
import math
from osgeo import gdal

from osgeo import gdal,ogr,osr
import affine
import numpy as np

raster=r'test-top-right.tif'
longitude = 9.874404
latitude = 52.442347
src = gdal.Open(raster)

x = longitude 
y = latitude

from osgeo import gdal, osr

width = src.RasterXSize
height = src.RasterYSize

point_srs = osr.SpatialReference()
point_srs.ImportFromEPSG(4326) # hardcode for lon/lat

point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)     

file_srs = osr.SpatialReference()
file_srs.ImportFromWkt(src.GetProjection())

ct = osr.CoordinateTransformation(point_srs, file_srs)

point_x = x #long
point_y = y #lat
mapx, mapy, z = ct.TransformPoint(point_x, point_y)

gt_inv = gdal.InvGeoTransform(src.GetGeoTransform())
pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)

# round to pixel
pixel_x = round(pixel_x)
pixel_y = round(pixel_y)

# clip to file extent
pixel_x = max(min(pixel_x, width-1), 0)
pixel_y = max(min(pixel_y, height-1), 0)

print(pixel_x, pixel_y)



#test-top-right.tif
longitude = 9.874404
latitude = 52.442347

xMax= 9.882972
yMax=52.454889

xMin = 9.853202
yMin = 52.437119


bbox = [xMin, yMin, xMax, yMax]
pixelWidth = 10000
pixelHeight = 10000
bboxWidth = bbox[ 2 ] - bbox[ 0 ]
bboxHeight = bbox[ 3 ] - bbox[ 1 ]

widthPct =( longitude - bbox[ 0 ] ) / bboxWidth
heightPct = ( latitude - bbox[ 1 ] ) / bboxHeight
xPx = math.floor( pixelWidth * widthPct )
yPx = math.floor( pixelHeight * ( 1 - heightPct ) )

print(xPx, yPx)