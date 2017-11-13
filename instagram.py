import requests
import json

headers = {'Host': 'www.instagram.com',
           'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0)
           Gecko/20100101 Firefox/56.0''',
           'Accept': '*/*',
           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br',
           'X-Requested-With': 'XMLHttpRequest',
           'Connection': 'keep-alive'}

# ======== Users Data ======== #
#address = '''https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables={"id":"285580799","first":50}''' 
#req = requests.get(address, headers)
#print req.text
#data = json.loads(req.text)
#print data['data']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['shortcode']


# ======== Comments =========#

#address = '''https://www.instagram.com/graphql/query/?query_id=17852405266163336&variables={"shortcode":"BaTz20CFtLX","first":20}''' 
#req = requests.get(address, headers)
#print req.text
#data = json.loads(req.text)
#print data['data']['shortcode_media']['edge_media_to_comment']['edges'][0]['node']['owner']['id']

# ========= Likes ========== #

address = '''https://www.instagram.com/graphql/query/?query_id=17864450716183058&variables={"shortcode":"BaTz20CFtLX","first":100}''' 
req = requests.get(address, headers)
#print req.text
data = json.loads(req.text)
print data['data']['shortcode_media']['edge_liked_by']['edges'][0]['node']['id']













