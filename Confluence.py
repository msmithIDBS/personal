import requests
import mimetypes
from requests.auth import HTTPBasicAuth

baseurl = 'https://idbs-hub.atlassian.net'
api_url = '/wiki/rest/api/content/3018391709/child/attachment/att3468787746/data'
# api_url = '/wiki/rest/api/content/3018391709/child/attachment'
apikey = 'BzAruZiuJGgiC2prOI6CA93F'
auth = HTTPBasicAuth('msmith@idbs.com', 'BzAruZiuJGgiC2prOI6CA93F')
page_id = '3018391709'
attachment_id = 'att3427172472'

# apikey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
headers = {'X-Atlassian-Token': 'no-check'}  # , 'Authorization': "Bearer {}".format(apikey)}
# data = {'file': image_file}
file = 'roadmap_output.jpg'

# determine content-type
content_type, encoding = mimetypes.guess_type(file)
if content_type is None:
    content_type = 'image/jpeg'

# provide content-type explicitly
files = {'file': (file, open(file, 'rb'), content_type)}

resurl = baseurl + api_url
post_response = requests.post(resurl, auth=auth, headers=headers, files=files)
# get_response = requests.get(resurl, auth=auth, headers=headers)

print(post_response)
# print(get_response.content)