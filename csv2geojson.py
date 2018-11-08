#!/usr/bin/env python3

import pandas as pd
from calc_path_distance import *
from geojson_utils import gcj02towgs84 as gcj2wgs 
import sys
p = pd.read_csv(sys.argv[1])
loci = list(p).index('location')
fpj = lambda a: gcj2wgs(*a)
if len(sys.argv) < 4: fpj = lambda a: a

save_pois([
    {
        'type':'Feature', 
        'geometry': {'type':'Point', 'coordinates': fpj([float(_) for _ in r[loci].split(',')]) }, 
        'properties': dict([(k, r[ki]) for ki, k in enumerate(p)])
    } for r in p.values], sys.argv[2])