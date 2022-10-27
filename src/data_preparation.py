import geojson
import data_classes as dc

class Dataprep:
    cycleways=[]
    streets=[]

    def addstreet(self, feature:any, nodes:list, lanes:int):
        lanes = int(round(float(lanes)))
        bike_right= 'cycleway:right' in feature['properties']
        bike_left= 'cycleway:left' in feature['properties'] 

        if 'cycleway:both' in feature['properties'] or ('sidewalk' in feature['properties'] and feature['properties']['sidewalk']=="both"):
            bike_right= True
            bike_left= True

        self.streets.append(dc.Street(nodes, lanes, bike_right, bike_left))

def fetchData(path) -> list: 
    dataprep=Dataprep()

    #read export file as geojson
    with open(path, encoding='utf-8') as f:
        gf = geojson.load(f)

    #iterate over features and add to corresponding class
    for feature in gf['features']:

        #add all nodes of feature
        nodes = []
        for coordinate in feature['geometry']['coordinates']:

            #PYTHON AUTOMATICALLY ROUNDES THE COORDINATES
            lon = coordinate[0]
            lat = coordinate[1]
            nodes.append(dc.Node(lat, lon))

        #decision if street or cycleway
        if 'lanes' in feature['properties']:
            lanes=feature['properties']['lanes']
            dataprep.addstreet(feature, nodes, lanes)

        elif 'lane_markings' in feature['properties']:
            lanes=2
            dataprep.addstreet(feature, nodes, lanes)

        else:
            dataprep.cycleways.append(dc.CycleWay(nodes))
    
    ret = dataprep.cycleways
    ret.extend(dataprep.streets)
    return ret