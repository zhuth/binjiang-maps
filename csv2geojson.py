#!/usr/bin/env python3

import pandas as pd
from calc_path_distance import *
import sys
p = pd.read_csv(sys.argv[1])
loci = list(p).index('location')
save_pois([
    {
        'type':'Feature', 
        'geometry': {'type':'Point', 'coordinates': [float(_) for _ in r[loci].split(',')]}, 
        'properties': dict([(k, r[ki]) for ki, k in enumerate(p)])
    } for r in p.values], sys.argv[2])