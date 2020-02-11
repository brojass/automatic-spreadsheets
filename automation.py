import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import re
from time import sleep

CLIENT_EMAIL = 'Google sheets ADE automation-9f128e1e2df4.json'
SPREADSHEET_FILE_NAME = 'Names for automation sheet'
CURRENT_CSV_FILE = 'current.csv'
IOC_CSV_FILE = 'ioc.csv'
SUPPORT_CSV_FILE = 'support.csv'


def find_in_support(ioc_dict):
    """
    Function that iterates over the ioc_dict and also read the support.csv file to find the dependencies version
    available associated to an specific IOC given in ioc_dict.
    :param ioc_dict: Dictionary of dependencies finded on the given IOC lines.
    :type ioc_dict: dict
    :return: A dictionary with all dependencies finded in support.csv file that depend each IOC of current.csv file.
    :rtype: dict
    """
    individual_dependencies_dict = {}
    ioc = ioc_dict['R3.14.12.8']
    version = ioc_dict[' ']
    super_key = ioc + ' ' + version
    supp_line_dict = {}
    with open(SUPPORT_CSV_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            for key, value in ioc_dict.items():

                if line['R3.14.12.8'] == key and line[' '] == value:
                    supp_line_key = key + ' ' + value
                    individual_dependencies_dict[supp_line_key] = line

    supp_line_dict[super_key] = individual_dependencies_dict
    return supp_line_dict


def find_in_ioc(dict_current_line):
    """
    Function that iterates and read the ioc.csv file to find the dependencies version associated to an specific line
    given in current.csv file. The line represent the name and version of IOC.
    :param dict_current_line: Specific line of current.csv file that represent the name and version of IOC.
    :type dict_current_line: dict
    :return: Dependencies finded in the given IOC line.
    :rtype: dict
    """
    ioc_present_dependencies_dict = {}
    ioc = dict_current_line["IOC"]
    version = dict_current_line['version']
    with open(IOC_CSV_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            if line['R3.14.12.8'] == ioc and line[' '] == version:

                for key, value in line.items():
                    ioc_present_dependencies_dict[key] = value

    return ioc_present_dependencies_dict


def setup_csv_file(current_file):
    """
    This function read the current.csv file and for each line search the dependencies in ioc.csv and support.csv files.
    First, with the help of def find_in_ioc() that iterates over each line of current.csv, and then with
    find_in_support() that iterates over the dependencies find in ioc.csv file.
    :param current_file: current.csv file.
    :type current_file: str
    :return: Two list with all dependencies finded on ioc.csv and support.csv files that depend each line of
    current.csv file.
    :rtype: tuple
    """
    final_supp_list = []
    final_ioc_list = []
    with open(current_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        if current_file == CURRENT_CSV_FILE:
            for line in csv_reader:

                if line['maturity'] == 'prod' or line['maturity'] == 'work' and re.search(r'-cp-ioc$', line['IOC']):
                    ioc_dependencies_dict = find_in_ioc(line)
                    if ioc_dependencies_dict:
                        support_present_dict = find_in_support(ioc_dependencies_dict)
                        final_ioc_list.append(ioc_dependencies_dict)
                        final_supp_list.append(support_present_dict)

    return final_ioc_list, final_supp_list


def basic_configuration(cl_email, sp_sheet_file, index_sheet):
    """
    Function that setup the API with an specific spreadsheet file in Google Docs. As result, we have access
    to the content of the file for insert, modified or eliminated rows.
    :param index_sheet: index that indicate the position of the sheet to open.
    :type index_sheet: int
    :param cl_email: .json generated by Google Cloud Platform that contain the private key.
    :type cl_email: str
    :param sp_sheet_file: Name of the spreadsheet file.
    :type sp_sheet_file: str
    :return: The content of the spreadsheet file.
    :rtype: tuple
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(cl_email, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sp_sheet_file).get_worksheet(index_sheet)
    content = sheet.get_all_records()
    return sheet, content


def insert_into_spreadsheets(ioc, supp):
    """
    Function that insert into the SPREADSHEET_FILE_NAME all dependencies finded on ioc.csv and support.csv files that
    depend each line of current.csv file.
    :param supp: List of dependencies existing on the given IOC lines.
    :type supp: list
    :param ioc: List of dependencies finded on the given IOC lines.
    :type ioc: list
    """
    sheet_position = 0
    column_line = ['IOC']

    for k, v in ioc[0].items():
        if re.search(r'-cp-ioc$', v):
            column_line.append('Epics')

        elif k == ' ':
            column_line.append('Version')
        else:
            column_line.append(k)
    sheet_back, content_back = basic_configuration(CLIENT_EMAIL, SPREADSHEET_FILE_NAME, sheet_position)
    index = 1
    sheet_back.insert_row(column_line, index)
    print(column_line)

    for ioc_item in ioc:
        row_line = []
        index += 1

        for k, v in ioc_item.items():

            if re.search(r'-cp-ioc$', v):
                row_line.append(v)
                row_line.append(k)
            else:
                row_line.append(v)

        sheet_back.insert_row(row_line, index)
        print(row_line)

    print('-------------------------------')
    sleep(100)
    sheet_position = 1
    sheet_back, content_back = basic_configuration(CLIENT_EMAIL, SPREADSHEET_FILE_NAME, sheet_position)
    index = 1

    for supp_item in supp:
        for key, value in supp_item.items():

            for k, v in value.items():
                row_line = [key, k]
                column_line = ['IOC', 'Dependency']

                for ke, val in v.items():
                    if not ke == 'R3.14.12.8':
                        if not re.search(r'^ ', ke):
                            column_line.append(ke)
                            row_line.append(val)

                sheet_back.insert_row(row_line, index)
                index += 1
                print(row_line)

    sheet_back.insert_row(column_line, 1)
    print(column_line)


# for item_list in supp_ioc_list:
#     sheet_back, content_back = basic_configuration(CLIENT_EMAIL, SPREADSHEET_FILE_NAME, sheet_position)
#     sheet_position += 1
#     index = 1
#
#     for item in item_list:
#         print(item)
#         new_line = item
#         sheet_back.insert_row(new_line, index)
#         index += 1


if __name__ == '__main__':

    # Read csv files and filter the dependencies available for an IOC
    support_list = []
    ioc_list = []
    try:
        ioc_list, support_list = setup_csv_file(CURRENT_CSV_FILE)
    except FileNotFoundError as e:
        print(e)
        exit(0)

    # Insert on SPREADSHEET_FILE_NAME the lists that have the dependencies available for an IOC
    try:
        insert_into_spreadsheets(ioc_list, support_list)

    except gspread.exceptions.SpreadsheetNotFound as e:
        # print(e)
        print('Spreadsheet NotFound: "' + SPREADSHEET_FILE_NAME + '"')
        exit(0)
    except FileNotFoundError as e:
        print(e)
        exit(0)
