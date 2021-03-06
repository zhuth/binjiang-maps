#!/usr/bin/env python3
# coding: utf-8

import requests
import json
import time
import sys
import math
import os, shutil
from urllib.parse import quote

def save_pois(fs, fn):
    res={
        "type": "FeatureCollection",
        "features": fs }    
    with open(fn,'w') as fo:
        fo.write(json.dumps(res))
        

def bd2gcj(lon, lat):
    x_pi = math.pi * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lon = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [ gg_lon, gg_lat ]
    
    
from geojson_utils import gcj02towgs84 as gcj2wgs 
    
    
def bd2wgs(lon, lat):
    return gcj2wgs(*bd2gcj(lon, lat))


import amapconfig


def amap_poi(city, type):
    u = 'https://restapi.amap.com/v3/place/text?key=%s&keywords=&citylimit=true&city={}&types={}&page={}' % (amapconfig.apikey,)
    print(citycode, category)
    pages = 1
    fs = []
    i = 0
    while i < pages:
        print(len(fs), '{}/{}'.format(i, pages))
        w=u.format(citycode, category + '00', i)
        time.sleep(0.1)
        j=requests.get(w).content
        j=json.loads(j)
        fs += [{'type':'Feature', 'geometry': {'type':'Point', 'coordinates': [[float(_) for _ in r['location'].split(',')]]}, 'properties':{'name':r['name'], 'region': citycode, 'biz':r['typecode'] + ' ' + r['type']}} for r in j['pois']]
        i += 1
        pages = int(math.ceil(int(j['count']) / 20))
    return fs
    
    
def amap_geocode(city, address):
    if isinstance(address, list):
        address = '|'.join(address)
    batch = '|' in address
    u = 'https://restapi.amap.com/v3/geocode/geo?key={}&city={}&address={}&batch={}'.format(amapconfig.apikey, city, address, 'true' if batch else 'false')
    j = json.loads(requests.get(u).content)
    if 'geocodes' in j:
        j = [_['location'] for _ in j['geocodes']]
    return j
    

if __name__ == '__main__':
    # keyword = sys.argv[1]
    # kw  = quote(keyword)
    import amapconfig
    fs = []
    
    if True:

        if os.path.exists('docs/geojsons/output.geojson'):
            shutil.move('docs/geojsons/output.geojson', 'docs/geojsons/output{}.geojson'.format(hash(time.time())))

        for citycode in [
            310101,310104,310105,310106,
            310107,310109,310110,310112,
            310113,310114,310115,310116,
            310117,310118,310120,310151]:
            for category in amapconfig.factory:
                fs += amap_poi(citycode, category)
                save_pois(fs, 'docs/geojsons/output.geojson')
    
    import glob
    from collections import defaultdict

    outputs = glob.glob('docs/geojsons/output*.geojson')
    fs = defaultdict(list)
    fsh = set()
    for output in outputs:
        j=json.load(open(output))
        for f in j['features']:
            f['geometry']['coordinates'] = gcj2wgs(*f['geometry']['coordinates'][0])
            h = repr(f['geometry']['coordinates'][0]) + f['properties']['name']
            if h not in fsh:
                fsh.add(h)
                fl = f['properties']['biz'].split(' ')[0].split('|')
                f['properties']['pty'] = fl[0][:4]
                for fll in fl:
                    fs[fll[:4]].append(f)

    fss = []
    for k, v in fs.items():
        save_pois(v, 'docs/geojsons/sh-' + k + '.geojson')
        fss += v

    save_pois(fss, 'docs/geojsons/sh.geojson')
