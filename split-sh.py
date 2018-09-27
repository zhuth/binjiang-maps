#!/usr/bin/env python3

from calc_path_distance import *
from collections import defaultdict

gj=read_pois('docs/geojsons/sh')
g = defaultdict(list)

for f in gj:
    for b in f['properties']['biz'].split(' ')[0].split('|'):
        g[b].append(f)
        
for k, fs in g.items():
    save_pois(fs, 'docs/geojsons/sh-' + k + '.geojson')