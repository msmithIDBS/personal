import requests
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap


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

def map_generate(initiative_dictionary):
    # create the roadmap
    initiatives = initiative_dictionary #["Sample Management Launch 1", "BioProcess Equipment Integration", "Scientific Insights"]
    f = open('co-ordinates.json')
    coordinates = json.load(f)
    annotationarray = {}

    #find the length of the line
    initiative_length = (len(coordinates.keys())-1) / len(initiatives.keys())
    print(initiative_length)

    this_initiative_length = initiative_length
    for initiative in initiatives:
        initiative_name = initiatives[initiative]['name']
        #if initiatives[initiative]['status'] ==
        intiative_lookup = str(int(round(this_initiative_length, 0)))
        tempdict = {'p': coordinates[intiative_lookup]['p'], 'x': coordinates[intiative_lookup]['x'], 'y': coordinates[intiative_lookup]['y']}
        annotationarray[initiative_name] = tempdict
        this_initiative_length = this_initiative_length + initiative_length

    print(annotationarray)
    image = Image.open('roadmap.png')
    pin_image = Image.open('roadmap_pin.png')
    mask_im = Image.open('roadmap_mask.png').resize(pin_image.size).convert('L')

    back_image = image.copy()


    font = ImageFont.truetype('calibri.ttf', 10, encoding='unic')
    for annotation in annotationarray:
        print(annotation)
        annotationlist = annotationarray[annotation]
        text_position = annotationlist['p']

        image_x = annotationlist['x'] -17
        image_y = annotationlist['y'] - 17
        back_image.paste(pin_image, (image_x, image_y), mask_im)

        draw = ImageDraw.Draw(back_image)
        w, h = draw.textsize(annotation)

        if text_position == 'a':
            text_x = annotationlist['x'] - (w/2)
            text_y = annotationlist['y'] - 35
        elif text_position == 'b':
            text_x = annotationlist['x'] - (w/2)
            text_y = annotationlist['y'] + 18
        elif text_position == 'r':
            text_x = annotationlist['x'] + 20
            text_y = annotationlist['y'] - 8
        elif text_position == 'l':
            text_x = annotationlist['x'] - w - 20
            text_y = annotationlist['y'] - 8

        draw.text((text_x, text_y), annotation, fill='#000000', font=font)

    back_image.show()
    # image.save('roadmap.png','PNG')


def poll_aha():
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

if __name__ == "__main__":
    solutions_work = poll_aha()
    #solutions_work = {'6986619487959771721': {'name': 'Allow for seamless transfer of cost predictions between Development and Manufacturing', 'status': 'backlog_[define]', 'priority': 'Later'}, '6985148671268327090': {'name': 'Deprecate the need for the BRD (Results Hub) from all Strategic Solutions', 'status': 'selected_for_roadmap', 'rice': 6, 'technical': ['EWB Core', 'Insights', 'Workflows'], 'pillar': ['EWB Core', 'Insights', 'Workflows'], 'priority': 'Next'}, '6982858184126869585': {'name': 'Extend BioA Capabilities to cover ICH M10 Quantitative LCMS Analysis', 'status': 'selected_for_roadmap', 'rice': 6, 'technical': ['Workflows'], 'pillar': ['Workflows'], 'priority': 'Next'}}
    print(solutions_work)
    map_generate(solutions_work)
