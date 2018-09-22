import json
import sys

fs = []
for f in sys.argv[2:]:
    fs += json.load(open(f))['features']
    
with open(sys.argv[1],'w') as fo:
    fo.write(json.dumps({
                "type": "FeatureCollection",
                "features": fs }))
                    