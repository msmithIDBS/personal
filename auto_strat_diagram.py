import requests
import json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import datetime
import textwrap
from requests.auth import HTTPBasicAuth
import mimetypes

def get_call(api_url, return_name):
    baseurl = 'https://idbs-hub.aha.io'
    apikey = '07a429f2762cf51a4a027024bda48652a4554ef856335a58629ad5d99653ef87'
    headers = {'accept': 'application/json',
               'contentType': 'application/json',
               'authorization': "Bearer {}".format(apikey)}

    resurl = baseurl + api_url
    init_pages = []

    for pagination in range(1, 6): #Need to make the max range dynamic
        params = 'fields=name,workflow_status:name,custom_fields&page=' + str(pagination)
        get_response = requests.get(resurl, headers=headers, params=params)
        json_data = get_response.json()
        next_init_pages = json_data[return_name]

        for i in next_init_pages:
            init_pages.append(i)

    return init_pages

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
        rel_date = datetime.datetime.strptime('2999-01-01', '%Y-%m-%d')

        for init in initiatives:
            if rel_date > datetime.datetime.strptime(initiatives[init]['external_release_date'], '%Y-%m-%d'):
                rel_date = datetime.datetime.strptime(initiatives[init]['external_release_date'], '%Y-%m-%d')
                rel_name = init

        initiative_name = initiatives[rel_name]['name']
        intiative_lookup = str(int(round(this_initiative_length, 0)))

        annotation_x = int(coordinates[intiative_lookup]['x'])
        annotation_y = int(coordinates[intiative_lookup]['y'])
        annotation_t = initiatives[rel_name]['launch_confidence']
        annotation = initiative_name

        if type == 'i':
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
        elif type == 'w':
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

        if type == 'i':
            if w > 188:
                text_x = annotation_x - 190
            else:
                text_x = annotation_x - w - 30

            text_y = annotation_y - 8
        elif type == 'd':
            text_x = annotation_x + 25
            text_y = annotation_y - 5
        elif type == 'w':
            text_x = annotation_x
            text_y = annotation_y + 20
        elif type == 'c':
            text_x = annotation_x - 5
            text_y = annotation_y + 25

        # draw text
        lines = textwrap.wrap(annotation, width=26)
        for line in lines:
            line_width, line_height = font.getsize(line)
            draw.text((text_x, text_y), line, font=font, fill='#FFFFFF')
            text_y += line_height

        this_initiative_length = this_initiative_length + initiative_length

        initiatives.pop(rel_name)
        x += 1

def poll_aha_goals():
    apiurl = '/api/v1/initiatives'

    response = get_call(apiurl, 'initiatives')
    #json_response = json.loads(response)
    goals = response

    solution_goals = {}
    for goal in goals:
        d_minus = 0
        is_solution = False
        properties = {'name': goal['name'],
                      'launch_confidence': '',
                      'pillar': 'Other'
                      }

        if 'custom_fields' in goal:
            for custom_field in goal['custom_fields']:
                if custom_field['key'] == 'market':
                    if custom_field['value'] == 'BPLM' or custom_field['value'] == 'Both':
                        is_solution = True

                if custom_field['key'] == 'now_next_later':
                    if custom_field['value'] == 'Now':
                        properties['launch_confidence'] = 'Confirmed'
                    elif custom_field['value'] == 'Next':
                        properties['launch_confidence'] = 'Estimated'
                    else:
                        properties['launch_confidence'] = 'Projected'

                if custom_field['key'] == 'pillar':
                    if len(custom_field['value']) != 0:
                        properties['pillar'] = custom_field['value'][0]

                if custom_field['key'] == 'idbs_rice_score':
                    d_minus = float(custom_field['value'])

        if goal['status'] == 'finished' or goal['status'] == 'rejected' or goal['status'] == 'ideas_backlog':
            properties['status'] = goal['status']
            properties['released'] = True
            properties['launch_confidence'] = 'Projected'
        elif goal['status'] == 'complete':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = -500 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        elif goal['status'] == 'in_progress_(resourced)' or goal['status'] == 'in_progress_(un-resourced)':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = 0 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        elif goal['status'] == 'roadmap_backlog':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = 500 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        elif goal['status'] == 'discovery_execution':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = 1000 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        elif goal['status'] == 'discovery_backlog':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = 1500 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        elif goal['status'] == 'idea scoring':
            properties['status'] = goal['status']
            properties['released'] = False
            ds_minus = 2000 - d_minus
            temp_date = datetime.date.today() + datetime.timedelta(days=ds_minus)
            properties['external_release_date'] = temp_date.strftime("%Y-%m-%d")
        else:
            properties['status'] = goal['status']
            properties['released'] = True
            properties['launch_confidence'] = 'Projected'

        if is_solution is True:
            solution_goals[goal['id']] = properties

    return solution_goals

def poll_aha_releases():
    all_apiurl = '/api/v1/products/6979594302160412111/releases'

    all_response = get_call(all_apiurl, 'releases')
    #all_json_response = json.loads(all_response)

    all_releases = all_response # all_json_response['releases']

    releases = {}

    is_solution = False
    for all_release in all_releases:
        release_id = all_release['id']
        apiurl = '/api/v1/releases/{}'.format(release_id)

        response = get_call(apiurl, 'release')
        #json_response = json.loads(response)
        temp_release = response # json_response['release']

        properties = {'name': temp_release['name'],
                      'external_release_date': temp_release['external_release_date'],
                      'released': temp_release['released'],
                      'launch_confidence': '',
                      'pillar': 'Other'
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

    return post_response

if __name__ == "__main__":
    # all_solutions_work = poll_aha_releases()
    all_solutions_work = poll_aha_goals()
    workflows_pillar = {}
    insights_pillar = {}
    integrations_pillar = {}
    other_pillar = {}

    # print(all_solutions_work)
    for x, y in all_solutions_work.items():

        if y['pillar'] == 'Workflows' and y['released'] is False:
            workflows_pillar[x] = y
        if y['pillar'] == 'Integrations' and y['released'] is False:
            insights_pillar[x] = y
        if y['pillar'] == 'Insights' and y['released'] is False:
            integrations_pillar[x] = y
        if y['pillar'] == 'Other' and y['released'] is False:
            other_pillar[x] = y

    image = Image.open('roadmap.png')
    back_image = image.copy()

    #print(workflows_pillar)
    if len(workflows_pillar) > 0:
        map_generate(workflows_pillar, 'workflow_co-ordinates.json', 'w', back_image)

    #print(insights_pillar)
    if len(insights_pillar) > 0:
        map_generate(insights_pillar, 'workflow_co-ordinates.json', 'i', back_image)

    #print(integrations_pillar)
    if len(integrations_pillar) > 0:
        map_generate(integrations_pillar, 'workflow_co-ordinates.json', 'd', back_image)

    #print(other_pillar)
    if len(other_pillar) > 0:
        map_generate(other_pillar, 'workflow_co-ordinates.json', 'c', back_image)

    back_image.save('roadmap_output.png')
    jpeg_image = back_image.convert('RGB')
    jpeg_image.save('roadmap_output.jpg')

    update_confulence('roadmap_output.jpg')

    back_image.show()
