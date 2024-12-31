import requests
from bs4 import BeautifulSoup
import re


def readHtml():
    url = 'https://www.idejihuo.com/'
    response = requests.get(url)
    unique_values = set()

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        inputs = soup.find_all('input')

        for input_element in inputs:
            value = input_element.get('value')

            # 如果 value 属性存在且是一个可能的 HTML 或者 URL
            if value is not None:
                # 假设 value 可能是一个 URL 或者 HTML 内容
                if re.match(r'^http[s]?://', value):  # 判断是否是URL
                    # 如果是URL, 发起请求获取该页面内容
                    sub_response = requests.get(value)
                    if sub_response.status_code == 200:
                        sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                        # 查找包含数据的 div
                        accordion_div = sub_soup.find('div', class_='accordion-body mt-3')
                        if accordion_div:
                            unique_values.add(accordion_div.get_text(strip=True))  # 提取纯文本内容
                else:
                    # 如果是普通的字符串内容，直接添加
                    unique_values.add(value)
    else:
        print(f'网页请求失败，状态码：{response.status_code}')

    return unique_values


def writeDoc(licenses):
    with open('JetBrainsLicense.txt', 'w', encoding='utf-8') as file:
        for license in licenses:
            file.write(license + '\n')


if __name__ == '__main__':
    licenses = readHtml()
    writeDoc(licenses)