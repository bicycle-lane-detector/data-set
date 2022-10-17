from dataclasses import dataclass

@dataclass(frozen=True, init=True)
class Node:
    lat:float
    lon:float
    
'''CycleWay is a dedicated bicycle road, that does not have to be adjusted'''
@dataclass(frozen=True, init=True)
class CycleWay:
    nodes:list

'''Street is a regular street that has cycle lanes or tracks on the side'''
@dataclass(frozen=True, init=True)
class Street:
    nodes:list
    n_car_lanes:int
    bike_right:bool
    bike_left:bool
