import requests
from requests.auth import HTTPBasicAuth
import json

def get_call(url, query):
    auth = HTTPBasicAuth('msmith@idbs.com', 'BzAruZiuJGgiC2prOI6CA93F')
    headers = {'Accept': 'application/json'}

    response = requests.request('GET', url, headers=headers, params=query, auth=auth).json()

    return response

def put_call(url, payload):
    auth = HTTPBasicAuth('msmith@idbs.com', 'BzAruZiuJGgiC2prOI6CA93F')
    headers = {'Accept': 'application/json', "Content-Type": "application/json"}

    response = requests.request("PUT", url, data=payload, headers=headers, auth=auth)

if __name__ == "__main__":
    postdict = {}

    #get the issues from the PLR board
    project = 'PLR'
    url = 'https://idbs-hub.atlassian.net/rest/api/3/search'
    query = {'jql': 'project = ' + project + ' AND type = initiative AND status != New'}
    response = get_call(url, query)
    PLRboard = response['issues']

    jirakeys = []
    for PLR in PLRboard:
        jirakeys.append(PLR['key'])

    #jirakeys = ['PLR-151']

    for init in jirakeys:
        url = 'https://idbs-hub.atlassian.net/rest/api/latest/issue/' + init + '/remotelink'
        query = {}
        response = get_call(url, query)

        initiative = response
        epic_id={}
        BIOAIDBS_Status = {'Backlog' : 0, 'Selected for Development' : 25, 'In Progress' : 50, 'Test/Review' : 75, 'Pending Acceptance' : 90, 'Done' : 100}
        BPLM_Status = {'To Do' : 0, 'POC or Wireframe' : 25, 'In Progress' : 50, 'Testing' : 60, 'IDBS Review' : 70, 'Document Updates' : 80, 'Done' : 100}
        SPM_Status = {'To Do': 0, 'In Progress': 50, 'Blocked/Hold': 50, 'Done': 100}

        'get the epics in the initiative'
        for epic in initiative:
            epic_id[epic['id']] = epic['object']['title']

        'get the status of the epics'
        ticketlist = []
        score = 0
        for key in epic_id.values():
            if key[:4] == 'BPLM':
                BOARD_Status = BPLM_Status
            elif key[:4] == 'BIOA':
                BOARD_Status = BIOAIDBS_Status
            elif key[:3] == 'SPM':
                BOARD_Status = SPM_Status
            else:
                break

            url = 'https://idbs-services.atlassian.net/rest/api/3/search'
            query = {'jql': 'key = ' + key}
            response = get_call(url, query)
            tickets = response['issues']
            score = score + BOARD_Status[tickets[0]['fields']['status']['name']]

            ticketlist.append(score)

        try:
            score = round(score / len(ticketlist), 0)
        except:
            score = 0

        postdict[init] = score

    #Post the status to PLR Board
    for key, value in postdict.items():
        url = 'https://idbs-hub.atlassian.net/rest/api/3/issue/' + key

        payload = json.dumps({"fields": {"customfield_12808":value}})

        response = put_call(url, payload)
