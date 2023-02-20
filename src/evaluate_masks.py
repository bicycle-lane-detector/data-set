from data_preparation import fetchData
import data_classes as dc



geotifs = ['osnabrueck.geojson', 'braunschweig.geojson', 'hannover.geojson', 'oldenburg.geojson']

osm_data = []

for geotif in geotifs:

    osm_data = osm_data + fetchData(geotif)

print("collected roads", len(osm_data))

cycleways = []
streets = []

for road in osm_data:
    if type(road) is dc.CycleWay:
        cycleways.append(road)
    if type(road) is dc.Street:
        streets.append(road)

print("cycleways thereof", len(cycleways))
print("streets thereof", len(streets))

nbCyclewayNodes = 0
for v in cycleways:
    nbCyclewayNodes += len(v.nodes)

nbStreetNodes = 0
for v in streets:
    nbStreetNodes += (int(v.bike_right) + int(v.bike_left)) *  len(v.nodes)

sum = nbCyclewayNodes + nbStreetNodes
print()
print("cycleway nodes", nbCyclewayNodes, nbCyclewayNodes / sum)
print("street nodes", nbStreetNodes, nbStreetNodes / sum)