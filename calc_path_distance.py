#!/usr/bin/env python3

from lxml import etree as ET
import re
import sys
import glob
import math
import numpy as np
import json
from amaplbs import save_pois
from shapely.geometry import Polygon
from pyproj import Proj, transform
EARTH_RADIUS = 6378137

MAX_DIST = 1000

paths = {}

def to_float(coord):
    return float(coord[0]), float(coord[1])
    
    
def get_dist(i, j):
    
    def deg_to_rad(deg):
        return deg * math.pi / 180.0
        
    b = deg_to_rad(i[0]-j[0])
    a = deg_to_rad(i[1]-j[1])
    s = 2 * math.asin(math.sqrt((math.sin(a/2)**2)+math.cos(deg_to_rad(i[1]))*math.cos(deg_to_rad(j[1]))*(math.sin(b/2)**2)))
    s *= EARTH_RADIUS
    return s
    

def get_len(coords):
    d = 0
    for i, j in zip(coords[:-1], coords[1:]):
        d += get_dist(i, j)
        
    return d
    
    
def polygon_area(coords):
    polygon = Polygon(coords)
    lon, lat = zip(*coords)
    pa = Proj("+proj=aea +lat_1=31.1 +lat_2=31.3 +lat_0=31.2 +lon_0=121.5")
    x, y = pa(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    from shapely.geometry import shape
    return shape(cop).area 
    

def combine_paths(pa, pb):
    #if (pa[0][1] > pa[-1][1]) == (pb[0][1] > pb[-1][1]):
    if get_dist(pa[-1], pb[0]) > get_dist(pa[-1], pb[-1]):
        return pa + pb[-1:0:-1] + [pb[0]]
    else:
        return pa + pb

        
def point_to_line(pt1, pt2, pt3):
    x1, y1 = pt1
    x2, y2 = pt2
    x, y = pt3
    cross = (x2 - x1) * (x - x1) + (y2 - y1) * (y - y1)
    if cross <= 0:
        return euc_dist((x, y), (x1, y1))

    d2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
    if cross >= d2:
        return euc_dist((x, y), (x2, y2))
    
    r = cross / d2;
    px = x1 + (x2 - x1) * r
    py = y1 + (y2 - y1) * r
    return math.sqrt((x - px) * (x - px) + (py - y1) * (py - y1));

        
def euc_dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x**2 + y**2)
        

def find_dist(coordinate, paths):
    dist = MAX_DIST
    for pt1, pt2 in paths:
        #print(euc_dist(pj(pt1), pj(pt2)))
        d1 = point_to_line(pt1, pt2, pj(coordinate))
        if d1 < dist: dist = d1
    return dist
    
    
def select_pois(fs, x):
    def print_t(*args):
        print('"' + '","'.join([str(_) for _ in args]) + '"')
        
    r = []
    for f in fs:
        if x(f['properties']['name']):
            r.append(f)
    return r
    

def read_pois(x):
    return json.load(open(x + '.geojson'))['features']

if __name__ == '__main__':
    for kml in glob.glob('*.kml'):
        r = ET.parse(kml).getroot()
        marks = r.findall('.//Placemark', namespaces=r.nsmap)
        for mark in marks:
            coords = mark.find('{http://www.opengis.net/kml/2.2}LineString')
            if coords is not None:
                name = mark.find('{http://www.opengis.net/kml/2.2}name').text
                coords = coords.find('{http://www.opengis.net/kml/2.2}coordinates')
                coords = [to_float(_.split(',')[:2]) for _ in re.split(r'\s', coords.text) if _ and ',' in _]
                paths[name] = coords

    # for _ in paths:
    #     print(_, get_len(paths[_]))

    # pudong = polygon_area(combine_paths(paths['浦东'], paths['浦东浦江']))
    # puxi = polygon_area(combine_paths(paths['浦西连结'], paths['浦西浦江']))
    # print(polygon_area(combine_paths(paths['浦西连结'], paths['浦东'])) - polygon_area(combine_paths(paths['浦西浦江'], paths['浦东浦江'])))
    # 
    # print(pudong / ((get_len(paths['浦东浦江'])+get_len(paths['浦东']))/2))
    # print(puxi / ((get_len(paths['浦西连结'])+get_len(paths['浦西浦江']))/2))
    # 
    # print(pudong / get_len(paths['浦东浦江']))
    # print(puxi / get_len(paths['浦西浦江']))
    # 
    # print(polygon_area(combine_paths(paths['pdresident'], paths['浦东'])) / get_len(paths['浦东']))
    # print(polygon_area(combine_paths(paths['pxident'], paths['浦西连结'])) / get_len(paths['浦西连结']))
    
    wgs84 = Proj('+proj=longlat +datum=WGS84 +no_defs') 
    epsg26715 = Proj(init='epsg:26715')
    pj = lambda pt: transform(wgs84, epsg26715, pt[0], pt[1])
    
    visited = set()
    pxlj = [pj(_) for _ in paths['浦西连结']]
    pd = [pj(_) for _ in paths['浦东']]
    paths = list(zip(pxlj[:-1], pxlj[1:])) + list(zip(pd[:-1], pd[1:]))
    
    for file in sys.argv[1:]:
        malls = read_pois(file)
        for mall in malls:
            descr = mall['properties']['name'] + '\t' + mall['properties']['pty']
            if descr in visited: continue
            visited.add(descr)
            coordinate = mall['geometry']['coordinates']
            dist = find_dist(coordinate, paths)
            if dist < MAX_DIST:
                print(descr + '\t' + str(dist))
