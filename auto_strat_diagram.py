import requests
from requests.auth import HTTPBasicAuth
import json
from PIL import Image, ImageDraw, ImageFont
from shutil import copyfile

def get_call(apiurl):
    baseurl = 'https://idbs-hub.aha.io'
    APIKey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
    username = 'msmith@idbs.com'
    headers = {'accept': 'application/json', 'accept': 'contentType: application/json', 'authorization': "Bearer {}".format(APIKey)}
    params = 'fields=name,workflow_status:name,custom_fields'

    url = baseurl + apiurl
    response = requests.get(url, headers=headers, params=params)

    return response.content

def label_contour_center(image, c):
    # Places some text over the contours
        M = cv2.moments(c)
        try:
            cx = int(M['m10'] / M['m00'])
        except:
            print("An exception occurred")

        try:
            cy = int(M['m01'] / M['m00'])
        except:
            print("An exception occurred")

        try:
            cv2.putText(image, "#{}".format(i + 1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, .3, (255,150,250), 1)
        except:
            print("An exception occurred")
        return image

if __name__ == "__main__":
    #Get a list of all the goals
    apiurl = '/api/v1/initiatives'
    #query = {'fields=name,reference_num,workflow_status'}

    response = get_call(apiurl)
    json_response = json.loads(response)

    goals = json_response['initiatives']

    solution_goals = {}
    for goal in goals:
        is_solution = False
        properties = {}

        properties['name'] = goal['name']
        properties['status'] = goal['status']

        if 'custom_fields' in goal:
            custom_fields = goal['custom_fields']
            for custom_field in custom_fields:
                if custom_field['key'] == 'primary_resource_domain':
                    if custom_field['value'] == 'Solutions':
                        is_solution = True

                if custom_field['key'] == 'now_next_later':
                    properties['priority'] = custom_field['value']

                if custom_field['key'] == 'idbs_rice_score':
                    properties['rice'] = custom_field['value']

                if custom_field['key'] == 'technical_or_solution_domain':
                    properties['technical'] = custom_field['value']

                if custom_field['key'] == 'technical_or_solution_domain':
                    properties['pillar'] = custom_field['value']

        if is_solution == True:
            solution_goals[goal['id']] = properties

    print(solution_goals)

    #create the roadmap
    annotationarray = {"now1": [234, 296],
                       "now2": [285, 344]
                      }

    image = Image.open('RDMP.jpg')
    draw  = ImageDraw.Draw(image)
    font  = ImageFont.truetype('arial.ttf', 20, encoding='unic')
    for annotation in annotationarray:
        annotationlist = annotationarray[annotation]
        x = annotationlist[0]
        y = annotationlist[1]

        draw.text( (x,y), u'Your Text', fill='#a00000', font=font)

    image.show()
    #image.save('roadmap.png','PNG')
