import os

import pandas

import requests
from bs4 import BeautifulSoup
from common_utils import BASE_URLS, parse_cases_table, get_pages_number, parse_cases_details_table


def scrap_cases():
        response = requests.get(BASE_URLS['Cases'].format("1"))

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_table(soup)

        data = pandas.DataFrame(res, columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                              'Main Activity'])

        data['Time-st'] = pandas.to_datetime('today').utcnow()

        try:
            os.makedirs('Cases')
        except FileExistsError:
            pass

        data.head(10).to_csv(f'Cases/cases.csv', index=False)

        pages = get_pages_number(soup)

        for i in range(2, pages+1):

            response = requests.get(BASE_URLS['Cases'].format(i))
            soup = BeautifulSoup(response.text, 'lxml')

            res = parse_cases_table(soup)
            res.pop()

            data = pandas.DataFrame(res,
                                    columns=['Case Number', 'Defendant\'s Name', 'Offence Date', 'Local Authority',
                                             'Main Activity'])
            data['Time-st'] = pandas.to_datetime('today').utcnow()
            data.head(10).to_csv(f'Cases/cases.csv', index=False, mode='a', header=False)


def scrap_cases_details():

    df = pandas.read_csv(f'Cases/cases.csv', sep='\t')

    for i in range(0, len(df)):
        case_number = df.iat[i, 0].split(',')[0]
        response = requests.get('https://resources.hse.gov.uk/convictions/case/case_details.asp?SF=CN&SV=' + case_number)

        soup = BeautifulSoup(response.text, 'lxml')
        res = parse_cases_details_table(soup)
        res.insert(0, case_number)

        try:
            new_df = pandas.DataFrame(
                [res],
                columns=[
                    'Case Number', 'Defendant', 'Description', 'Offence Date',
                    'Total Fine', 'Total Costs Awarded to HSE', 'Address', 'Region', 'Local Authority', 'Industry',
                    'Main Activity', 'Type of Location', 'HSE Group', 'HSE Directorate', 'HSE Area', 'HSE Division'
                ]
            )
            new_df['Time-st'] = pandas.to_datetime('today').utcnow()
        except ValueError:
            print('Can\'t create new dataframe!')
            continue

        new_df.head(10).to_csv(f'Cases/{case_number}.csv', index=False)
