#!/usr/bin/env python3
# coding: utf-8

import requests
import json
import time
import sys
import math
from urllib.parse import quote

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

# keyword = sys.argv[1]
# kw  = quote(keyword)
from amapconfig import apikey
u = 'https://restapi.amap.com/v3/place/text?key=%s&keywords=&citylimit=true&city={}&types={}&page={}' % (apikey,)
fs = []

if False:
    for citycode in [
        310101,310104,310105,310106,
        310107,310109,310110,310112,
        310113,310114,310115,310116,
        310117,310118,310120,310151]:
        for category in '''050100
050101
050102
050103
050104
050105
050106
050107
050108
050109
050110
050111
050112
050113
050114
050115
050116
050117
050118
050119
050120
050121
050122
050123
050200
050201
050202
050203
050204
050205
050206
050207
050208
050209
050210
050211
050212
050213
050214
050215
050216
050217
050300
050301
050302
050303
050304
050305
050306
050307
050308
050309
050310
050311
050400
050500
050501
050502
050503
050504
050600
050700
050800
050900'''.split('\n'):#[
            #'060101','060102','060103','060201','060202','060301','060302','060303','060304','060305','060306','060307','060308','060401','060402','060403','060404','060405','060406','060407','060408','060409','060411','060413','060414','060415','060501','060502','060601','060602','060603','060604','060605','060606','060701','060702','060703','060704','060705','060706','060901','060902','060903','060904','060905','060906','060907','061001','061101','061102','061103','061104','061201','061202','061203','061204','061205','061206','061207','061208','061209','061210','061211','061212','061213','061214','061301','061302','061401','070201','070202','070203','070301','070302','070303','070304','070305','070306','070401','070501','070601','070603','070604','070605','070606','070607','070608','070609','070610','070701','070702','070703','070704','070705','070706','071801','071901','071902','071903','072001','080101','080102','080103','080104','080105','080106','080107','080108','080109','080110','080111','080112','080113','080114','080115','080116','080117','080118','080119','080201','080202','080301','080302','080303','080304','080305','080306','080307','080308','080401','080402','080501','080502','080503','080504','080505','080601','080602','080603','140101','140102','140201','140300','140400','140500','140600','140700','140800','140900','141000','141100','141101','141102','141103','141104','141105','141200','141300','141400','141500'
            
        #]:
            if not category.endswith('00'): continue
            print(citycode, category)
            pages = 1
            i = 0
            while i < pages:
                print(len(fs), '{}/{}'.format(i, pages))
                w=u.format(citycode, category + '00', i)
                time.sleep(0.1)
                j=requests.get(w).content
                j=json.loads(j)
                fs += [{'type':'Feature', 'geometry': {'type':'Point', 'coordinates': [[float(_) for _ in r['location'].split(',')]]}, 'properties':{'name':r['name'], 'biz':r['typecode'] + ' ' + r['type']}} for r in j['pois']]
                i += 1
                pages = int(math.ceil(int(j['count']) / 20))

            res={
                "type": "FeatureCollection",
                "features": fs }    
            with open('output.geojson','w') as fo:
                fo.write(json.dumps(res))
        
import glob
from collections import defaultdict

outputs = glob.glob('output*.geojson')
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
    with open('sh-' + k + '.geojson','w') as fo:
        fo.write(json.dumps({
                "type": "FeatureCollection",
                "features": v }))
    fss += v

with open('sh.geojson','w') as fo:
    fo.write(json.dumps({
                "type": "FeatureCollection",
                "features": fss }))
                