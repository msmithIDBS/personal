import requests
import json
from PIL import Image, ImageDraw, ImageFont


def get_call(api_url):
    baseurl = 'https://idbs-hub.aha.io'
    apikey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
    # username = 'msmith@idbs.com'
    headers = {'accept': 'application/json',
               'contentType': 'application/json',
               'authorization': "Bearer {}".format(apikey)}
    params = 'fields=name,workflow_status:name,custom_fields'

    resurl = baseurl + api_url
    get_response = requests.get(resurl, headers=headers, params=params)

    return get_response.content


if __name__ == "__main__":
    # Get a list of all the goals
    apiurl = '/api/v1/initiatives'

    response = get_call(apiurl)
    json_response = json.loads(response)

    goals = json_response['initiatives']

    solution_goals = {}
    for goal in goals:
        is_solution = False
        properties = {'name': goal['name'], 'status': goal['status']}

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

        if is_solution is True:
            solution_goals[goal['id']] = properties

    # create the roadmap
    annotationarray = {"now1": [234, 296],
                       "now2": [285, 344]
                       }

    image = Image.open('RDMP.jpg')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', 20, encoding='unic')
    for annotation in annotationarray:
        annotationlist = annotationarray[annotation]
        x = annotationlist[0]
        y = annotationlist[1]

        draw.text((x, y), u'Your Text', fill='#a00000', font=font)

    image.show()
    # image.save('roadmap.png','PNG')
