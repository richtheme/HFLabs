import requests
from bs4 import BeautifulSoup
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'credentials.json'  # Your api credentials

spreadsheetId = '1H-wsDEbXGO22jkKrYMZM9TlbCS7P1Pf5gNs_y4tSW2g'
sheet_name = 'Sheet 1st'
sheetId = 0


def create_table_and_give_drive_access(service, http_auth, email):
    """ Creating spreadsheet instance and give edit access to drive for the given gmail """
    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': 'TestDoc', 'locale': 'ru_RU'},
        'sheets': [{'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': sheet_name,
            'gridProperties': {'rowCount': 100, 'columnCount': 15}}
        }]
    }).execute()

    spreadsheet_id = spreadsheet['spreadsheetId']
    print('https://docs.google.com/spreadsheets/d/' + spreadsheet_id)
    print('Ok')

    drive_service = apiclient.discovery.build('drive', 'v3', http=http_auth)
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={'type': 'user', 'role': 'writer', 'emailAddress': email},
        fields='id'
    ).execute()


def reset_table(service):
    """ Resetting the whole table """
    # Clear values
    range_all = '{0}!A1:Z'.format(sheet_name)
    body = {}
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheetId, range=range_all, body=body
    ).execute()

    # Clear styles
    body = {
        "requests": [
            {
                "updateCells": {
                    "range": {
                        "sheetId": sheetId
                    },
                    "fields": "userEnteredFormat"
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def parse_values():
    """ Parsing values for the table from confluence. Saving results to the list for easy recording to google
    spreadsheet """
    values = []

    url = 'https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', class_='confluenceTable')

    ths = table.find('thead').find_all('th')
    ths_list = []
    for th in ths:
        ths_list.append(th.text.strip())
    values.append(ths_list)

    trs = table.find('tbody').find_all('tr')
    trs_list = []
    for tr in trs:
        trs_row_list = []

        tds = tr.find_all('td')
        for td in tds:
            trs_row_list.append(td.text.strip())
        trs_list.append(trs_row_list)

    values.extend(trs_list)
    return values


def write_values(service, values):
    """ Writing parsed values """
    alphabet = ['A', 'B', 'C', 'D', 'E']
    len_rows = len(values)
    len_cols = len(values[0])

    service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "USER_ENTERED",
        # Data as user typed (Formulas work)
        "data": [
            {"range": sheet_name + "!A1:" + alphabet[len_cols - 1] + str(len_rows),
             "majorDimension": "ROWS",  # Firstly fill rows, then columns
             "values": values
             }
        ]
    }).execute()


def style_table(service):
    """ Set styles of the table """
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId,
        body={
            "requests":
                [
                    {  # Setting the width of 1st column (A)
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId,
                                "dimension": "COLUMNS",  # Setting column width
                                "startIndex": 0,  # Starts from zero
                                "endIndex": 1  # From column startIndex to endIndex - 1 (endIndex not included!)
                            },
                            "properties": {
                                "pixelSize": 200  # Width in pixels
                            },
                            "fields": "pixelSize"
                        }
                    },

                    {  # Setting the width of 2nd column (B)
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId,
                                "dimension": "COLUMNS",  # Setting column width
                                "startIndex": 1,  # Starts from zero
                                "endIndex": 2  # From column startIndex to endIndex - 1 (endIndex not included!)
                            },
                            "properties": {
                                "pixelSize": 400  # Width in pixels
                            },
                            "fields": "pixelSize"
                        }
                    },

                    {  # Set the font-size and background-color for 1st row (1 in spreadsheet)
                        "repeatCell":
                            {
                                "cell":
                                    {
                                        "userEnteredFormat":
                                            {
                                                "horizontalAlignment": 'CENTER',
                                                "backgroundColor": {
                                                    "red": 0.8,
                                                    "green": 0.8,
                                                    "blue": 0.8,
                                                    "alpha": 1
                                                },
                                                "textFormat":
                                                    {
                                                        "bold": True,
                                                        "fontSize": 14
                                                    }
                                            }
                                    },
                                "range":
                                    {
                                        "sheetId": sheetId,
                                        "startRowIndex": 0,
                                        "endRowIndex": 1,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 2
                                    },
                                "fields": "userEnteredFormat"
                            }
                    }
                ]
        }).execute()


def main():
    """ The main code """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )

    http_auth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth)
    values = parse_values()

    reset_table(service)
    write_values(service, values)
    style_table(service)


if __name__ == '__main__':
    main()
