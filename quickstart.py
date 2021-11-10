from __future__ import print_function

import json
import os.path
from pprint import pprint
from datetime import date

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1CHLl7uc_DQ4ysgi_ELMlKlb9ATvwAOdvOWUgiVbakbE'
SAMPLE_RANGE_NAME = 'B:C'
EXPENSES_CATEGORIES_RANGE = 'B22:C34'
INCOME_CATEGORIES_RANGE = 'H22:I27'
TRANSACTIONS_RANGE = 'Transactions'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Call the Sheets API
    # loadCategories(service, EXPENSES_CATEGORIES_RANGE)
    # loadCategories(service, INCOME_CATEGORIES_RANGE)
    # loadTransactions(sheet)
    # insertTransaction(sheet, amount, description, category)


def loadCategories(sheet, categories_range):
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=categories_range).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('Categories')
        for row in values:
            print(row[0])


def loadTransactions(sheet):
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=TRANSACTIONS_RANGE).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('Categories')
        for row in values:
            print(row[0], row[1], row[2], row[3])


def insertTransaction(amount, description, category):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()


    today = date.today().strftime("%d.%m.%Y")
    transaction = {
        "values": [
            [
                today,
                amount,
                description,
                category
            ]
        ]
    }
    result = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=TRANSACTIONS_RANGE,
                                   includeValuesInResponse=True, insertDataOption="INSERT_ROWS",
                                   valueInputOption="USER_ENTERED", body=transaction).execute()
    pprint(result)


if __name__ == '__main__':
    main()
