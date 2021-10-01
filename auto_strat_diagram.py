import requests
import json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import textwrap
from requests.auth import HTTPBasicAuth


def get_call(api_url):
    baseurl = 'https://idbs-hub.aha.io'
    apikey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
    headers = {'accept': 'application/json',
               'contentType': 'application/json',
               'authorization': "Bearer {}".format(apikey)}
    params = 'fields=name,workflow_status:name,custom_fields'

    resurl = baseurl + api_url
    get_response = requests.get(resurl, headers=headers, params=params)

    return get_response.content

def map_generate(initiative_dictionary, co_ordinates_file, type, back_image):
    # create the roadmap
    initiatives = initiative_dictionary
    f = open(co_ordinates_file)
    coordinates_temp = json.load(f)
    coordinates = coordinates_temp[type]

    font = ImageFont.truetype('arial.ttf', 12, encoding='unic')

    initiative_length = (len(coordinates.keys())-1) / len(initiatives.keys())

    pin_image = Image.open('roadmap_pin.png')
    mask_im = Image.open('roadmap_mask.png').resize(pin_image.size).convert('L')

    this_initiative_length = initiative_length/2

    init_loop = int(len(initiatives.keys()))
    x = 0
    while x < init_loop:

        rel_name = ''
        rel_date = datetime.strptime('2999-01-01', '%Y-%m-%d')

        for init in initiatives:
            if rel_date > datetime.strptime(initiatives[init]['external_release_date'], '%Y-%m-%d'):
                rel_date = datetime.strptime(initiatives[init]['external_release_date'], '%Y-%m-%d')
                rel_name = init

        initiative_name = initiatives[rel_name]['name']
        intiative_lookup = str(int(round(this_initiative_length, 0)))

        annotation_x = int(coordinates[intiative_lookup]['x'])
        annotation_y = int(coordinates[intiative_lookup]['y'])
        annotation_t = initiatives[rel_name]['launch_confidence']
        annotation = initiative_name

        if type == 'w':
            image_x = annotation_x - 17
            image_y = annotation_y - 17

            if annotation_t == 'Confirmed':
                pin_image = Image.open('roadmap_pin_w1.png')
            elif annotation_t == 'Estimated':
                pin_image = Image.open('roadmap_pin_w2.png')
            elif annotation_t == 'Projected':
                pin_image = Image.open('roadmap_pin_w3.png')
            else:
                pin_image = Image.open('roadmap_pin_w3.png')

        elif type == 'd':
            image_x = annotation_x - 17
            image_y = annotation_y - 17

            if annotation_t == 'Confirmed':
                pin_image = Image.open('roadmap_pin_d1.png')
            elif annotation_t == 'Estimated':
                pin_image = Image.open('roadmap_pin_d2.png')
            elif annotation_t == 'Projected':
                pin_image = Image.open('roadmap_pin_d3.png')
            else:
                pin_image = Image.open('roadmap_pin_d3.png')
        elif type == 'i':
            image_x = annotation_x - 17
            image_y = annotation_y - 17

            if annotation_t == 'Confirmed':
                pin_image = Image.open('roadmap_pin_i1.png')
            elif annotation_t == 'Estimated':
                pin_image = Image.open('roadmap_pin_i2.png')
            elif annotation_t == 'Projected':
                pin_image = Image.open('roadmap_pin_i3.png')
            else:
                pin_image = Image.open('roadmap_pin_i3.png')
        elif type == 'c':
            image_x = annotation_x - 17
            image_y = annotation_y - 17

            if annotation_t == 'Confirmed':
                pin_image = Image.open('roadmap_pin_c1.png')
            elif annotation_t == 'Estimated':
                pin_image = Image.open('roadmap_pin_c2.png')
            elif annotation_t == 'Projected':
                pin_image = Image.open('roadmap_pin_c3.png')
            else:
                pin_image = Image.open('roadmap_pin_c3.png')

        back_image.paste(pin_image, (image_x, image_y), mask_im)

        draw = ImageDraw.Draw(back_image)
        # w, h = draw.textsize(annotation)
        w, h = font.getsize(annotation)

        if type == 'w':
            text_x = annotation_x - 135
            text_y = annotation_y - 8
        elif type == 'd':
            text_x = annotation_x + 20
            text_y = annotation_y + 5
        elif type == 'i':
            text_x = annotation_x
            text_y = annotation_y + 20
        elif type == 'c':
            text_x = annotation_x - 5
            text_y = annotation_y + 25

        # draw text
        lines = textwrap.wrap(annotation, width=20)
        for line in lines:
            line_width, line_height = font.getsize(line)
            draw.text((text_x, text_y), line, font=font, fill='#FFFFFF')
            text_y += line_height

        this_initiative_length = this_initiative_length + initiative_length

        initiatives.pop(rel_name)
        x += 1

def poll_aha_goals():
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

    return solution_goals

def poll_aha_releases():
    all_apiurl = '/api/v1/products/6979594302160412111/releases'

    all_response = get_call(all_apiurl)
    all_json_response = json.loads(all_response)

    all_releases = all_json_response['releases']

    releases = {}

    is_solution = False
    for all_release in all_releases:
        release_id = all_release['id']
        apiurl = '/api/v1/releases/{}'.format(release_id)

        response = get_call(apiurl)
        json_response = json.loads(response)
        temp_release = json_response['release']
        print(temp_release)

        properties = {'name': temp_release['name'],
                      'external_release_date': temp_release['external_release_date'],
                      'released': temp_release['released'],
                      'launch_confidence': '',
                      'pillar': ''
                      }

        if 'custom_fields' in temp_release:
            for custom_field in temp_release['custom_fields']:
                if custom_field['key'] == 'market':
                    if custom_field['value'] == 'BPLM' or custom_field['value'] == 'Both':
                        is_solution = True

                if custom_field['key'] == 'launch_confidence':
                    properties['launch_confidence'] = custom_field['value']

                if custom_field['key'] == 'pillar':
                    properties['pillar'] = custom_field['value']

                if is_solution is True:
                    releases[temp_release['id']] = properties

    return releases

def update_confulence(image_file):
    baseurl = 'https://idbs-hub.atlassian.net'
    api_url = '/wiki/rest/api/content/3018391709/child/attachment/att3427172472/data'
    apikey = 'BzAruZiuJGgiC2prOI6CA93F'
    auth = HTTPBasicAuth('msmith@idbs.com', 'BzAruZiuJGgiC2prOI6CA93F')
    page_id = '3018391709'
    attachment_id = 'att3427172472'

    # apikey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
    headers = {'Accept': 'application/json'} #, 'Authorization': "Bearer {}".format(apikey)}
    data = {'file': image_file}

    resurl = baseurl + api_url
    get_response = requests.post(resurl, auth=auth, headers=headers, files={'file': image_file})

    print(get_response)

    return get_response

if __name__ == "__main__":
    # all_solutions_work = poll_aha_releases()
    # workflows_pillar = {}
    # insights_pillar = {}
    # integrations_pillar = {}
    # other_pillar = {}
    #
    # print(all_solutions_work)
    # for x, y in all_solutions_work.items():
    #
    #     if y['pillar'] == 'Workflows' and y['released'] is False:
    #         workflows_pillar[x] = y
    #     if y['pillar'] == 'Integrations' and y['released'] is False:
    #         insights_pillar[x] = y
    #     if y['pillar'] == 'Insights' and y['released'] is False:
    #         integrations_pillar[x] = y
    #     if y['pillar'] == 'Other' and y['released'] is False:
    #         other_pillar[x] = y
    #
    # image = Image.open('roadmap.png')
    # back_image = image.copy()
    #
    # print(workflows_pillar)
    # map_generate(workflows_pillar, 'workflow_co-ordinates.json', 'w', back_image)
    # map_generate(insights_pillar, 'workflow_co-ordinates.json', 'i', back_image)
    # map_generate(integrations_pillar, 'workflow_co-ordinates.json', 'd', back_image)
    # map_generate(other_pillar, 'workflow_co-ordinates.json', 'c', back_image)

    # back_image.save('roadmap_output.png')

    update_confulence('roadmap_output.png')

    # back_image.show()
