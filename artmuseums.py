import requests
f = open('urls.txt', 'w')
for _ in open('artmuseum.txt', encoding='utf-8').readlines():
	l = _.strip()
	r = requests.get('http://www.artlinkart.com/cn/search/listall/space/?q=' + l)
	c = r.content.decode('utf-8')
	if 'href="/cn/space/overview' in c:
		url = 'http://www.artlinkart.com' + c[c.find('href="/cn/space/overview')+6:]
		url = url[:url.find('"')]
		print(l)
		print(url)
	f.write(url + '\n')
f.close()