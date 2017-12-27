# -*- coding: utf-8 -*-
#from __future__ import print_function
"""
Google Drive Access Monitor
This script is based on the Google's quick start guide to Google Drive API: https://developers.google.com/drive/v3/web/quickstart/python
It uses the Oauth2 authentication mechanism and modifies the api call for file metadata. Every other change is entirely my own.
This script is developed as an internal tool for Strypes EOOD https://www.strypes.eu, part of the Dutch Tech Cluster
Author: Dzhovani Chemishanov
Version: 0.3
Date: 2017-12-04
License: Apache 2.0 http://www.apache.org/licenses/LICENSE-2.0

The script is intended for companies that are trying to review the security of their files in the cloud and the unintended exposure of sensitive information to the wider Internet. Paid services do exist, but  they require administrative access to the Google Drive which is unnecessary. The current script could be executed by any employee showing all public files and those visible to the entire company.
For security reasons, obtaining your own credentials for authentication is highly recommended.
"""

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def connection():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service


def is_exposed_to(item):
    """Checks all permissions of the file and returns the most exposing."""
    public_permission = ""
    permissions = item.get('permissions', [])
    for permission in permissions:
        if permission['type'] == 'anyone':
            public_permission = 'public'
            break
        elif permission['type'] == 'domain':
            public_permission = 'companyDomain'
    return public_permission


def entries():
    """Brows all  files visible for the current user and returns a filled in file with the relevant identifying information."""
    table_body = []
    token = None
    files_metadata_items = []
    fields_list = "nextPageToken, files(id, name, permissions, owners, webViewLink, webContentLink)"
    service = connection()

    api_call_results = service.files().list(
                   fields=fields_list).execute()
    files_metadata_items = api_call_results.get('files', [])
    while True:
        for item in files_metadata_items:
            exposed = is_exposed_to(item)
            if exposed != "":
                row = [item['name'].encode('ascii', "ignore"),
                     ', '.join([o['displayName'] for o in item['owners']]), # backward compatibility reasons
                     exposed,
                     item.get('webViewLink',
                     '-'), item.get('webContentLink', '-')]
                table_body.append(row)
        # check if the list of files has been exhausted
        # api_call_results is instantiated two times before and in the while loop
        # the idea is to account for the first call where there is no page token
        # if there is no token to a next page of results, break the connection
        # if token is not None, get new api_call_results
        # files_metadata_items could be empty list, because the api does not promise full page of results despite of search not finished
        token = api_call_results.get('nextPageToken', None)
        if not token:
            break
        api_call_results = service.files().list(
                   pageToken=token, fields=fields_list).execute()
        files_metadata_items = api_call_results.get('files', [])
    return table_body


def main():
    """Accepts the structured output and formats it for human use."""
    with open("results.txt", 'w') as f:
        f.write( '\n'.join([
                 ', '.join([cell for cell in row]) for row in entries()
        ]))


if __name__ == '__main__':
    main()