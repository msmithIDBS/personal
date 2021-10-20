import requests
from requests.auth import HTTPBasicAuth
import pandas as pd


def get_call(_url, _query):
    auth = HTTPBasicAuth('msmith@idbs.com', 'BzAruZiuJGgiC2prOI6CA93F')
    headers = {'Accept': 'application/json'}

    get_response = requests.request('GET', _url, headers=headers, params=_query, auth=auth).json()

    return get_response


if __name__ == "__main__":

    # get the issues from the PLR board
    project = 'PLR'
    url = 'https://idbs-hub.atlassian.net/rest/api/3/search'
    query = {'jql': 'project = ' + project + ' AND type = initiative AND status != New AND status != Done'}
    response = get_call(url, query)
    PLR_board = response['issues']
    pandas_data = {}

    jira_keys = []
    for PLR in PLR_board:
        jira_keys.append(PLR['key'])

    for init in jira_keys:
        url = 'https://idbs-hub.atlassian.net/rest/api/latest/issue/' + init + '/remotelink'
        query = {}
        response = get_call(url, query)

        initiative = response
        epics = []

        if not initiative:
            for epic in initiative:
                epics.append(epic['object']['title'])

            pandas_data[init] = epics

    df = pd.DataFrame.from_dict(pandas_data, orient='index')

    df.to_csv("output.csv")
