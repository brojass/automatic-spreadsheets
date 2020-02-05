import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import re

CLIENT_EMAIL = 'Google Docs automation-af72a95c9b76.json'
SPREADSHEET_FILE_NAME = 'Names for automation sheet'
CURRENT_CSV_FILE = 'current.csv'
IOC_CSV_FILE = 'ioc.csv'
SUPPORT_CSV_FILE = 'support.csv'


def find_in_support(ioc_dict):
    """

    :param ioc_dict:
    :type ioc_dict: dict
    :return:
    :rtype: list
    """
    dependencies_list = []
    print(ioc_dict)
    with open(SUPPORT_CSV_FILE) as csv_file:
        csv_reader = csv.reader(csv_file)
        for epics_version in csv_reader:
            epics = epics_version[0]
            version = epics_version[1]

            for key, value in ioc_dict.items():
                if key == epics and value == version:
                    print(epics, version)
                    dependencies_list.append(epics+' '+version)
    return dependencies_list


def find_in_ioc(dict_line):
    """

    :param dict_line:
    :type dict_line: dict
    :return:
    :rtype: dict
    """
    ioc_present_ALGO = {}
    ioc = dict_line["IOC"]
    version = dict_line['version']
    with open(IOC_CSV_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            if line['R3.14.12.8'] == ioc and line[' '] == version:

                for key, value in line.items():
                    if not re.search(r'^-', value):
                        ioc_present_ALGO[key] = value
    return ioc_present_ALGO


def setup_csv_file(file):
    """

    :param file:
    :type file: str
    :return:
    :rtype:
    """
    final_list = []
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        if file == CURRENT_CSV_FILE:
            for line in csv_reader:

                if line['maturity'] == 'prod':
                    # print('IOC: ' + line['IOC'] + ', version:' + line['version'])
                    ioc_dependencies = find_in_ioc(line)
                    if ioc_dependencies:
                        final_list.append(find_in_support(ioc_dependencies))
                else:
                    print('This is not prod maturity: ' + line['maturity'])
                    print(line)
    return final_list


def initial_configuration():
    """

    :return:
    :rtype: tuple
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_EMAIL, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_FILE_NAME).sheet1
    content = sheet.get_all_records()
    return sheet, content


if __name__ == '__main__':
    # print(setup_csv_file(CURRENT_CSV_FILE))
    for asd in setup_csv_file(CURRENT_CSV_FILE):
        print(asd)
# sheet_back, content_back = initial_configuration()
# print(content_back)
#
# new_line = ['Anakin', 'Skywalker', 'male', 'Tatooine']
# index = 3
# sheet.insert_row(new_line,index)
# sheet.delete_row(4)
