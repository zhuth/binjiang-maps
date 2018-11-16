import requests
import json

a=set()
while True:
	try:
		l=input()
		if not l: break
		a.add(l)
	except:
		break
		
a=list(a)
for i in range(0, len(a), 10):
	addrs = '|'.join(a[i:i+10])
	url = 'https://restapi.amap.com/v3/geocode/geo?batch=true&key=957264d0fdf6a73904dc32db02e3999d&address=' + addrs + '&city='
	j=json.loads(requests.get(url).content)
	for ad, g in zip(a[i:i+10], j['geocodes']):
		print(ad, g['formatted_address'], g['location'])