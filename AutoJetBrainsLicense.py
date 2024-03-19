# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


def readHtml():
    url = 'https://www.idejihuo.com/'
    response = requests.get(url)
    unique_values = set()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        inputs = soup.find_all('input')
        for input_element in inputs:
            value = input_element.get('value')
            if value is not None:
                unique_values.add(value)
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')

    return unique_values


def writeDoc(licenses):
    with open('JetBrainsLicense.txt', 'w') as file:
        for license in licenses:
            file.write(license + '\n')


if __name__ == '__main__':
    licenses = readHtml()
    writeDoc(licenses)
