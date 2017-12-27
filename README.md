# GDrive-Access-Monitor
This script is based on the Google's quick start guide to Google Drive API: https://developers.google.com/drive/v3/web/quickstart/python
It uses the Oauth2 authentication mechanism and modifies the api call for file metadata. Every other change is entirely my own.
This script is developed as an internal tool for Strypes EOOD https://www.strypes.eu, part of the Dutch Tech Cluster
and is published for public reuse

Author: Dzhovani Chemishanov
Version: 0.3
Date: 2017-12-04
License: Apache 2.0 http://www.apache.org/licenses/LICENSE-2.0

The script is intended for companies that are trying to review the security of their files in the cloud and the unintended exposure of sensitive information to the wider Internet. Paid services do exist, but  they require administrative access to the Google Drive which is unnecessary. The current script could be executed by any employee showing all public files and those visible to the entire company.
For security reasons, obtaining your own credentials for authentication is highly recommended.

The script lists all visible files on Google Drive that have any public or domain-wide permissions. The report is returned in a structured table that could be formatted in accordance with the user's needs. By default the results are sent to a results.txt file in the current directory. If you want the 

raw table, use:

from gdam import entries

