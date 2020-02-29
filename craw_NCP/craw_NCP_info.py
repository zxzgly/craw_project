# encoding:utf-8
# FileName: craw_NCP_info
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/2/12 21:06
# Description: 爬取每日NCP数据
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def init_selenium():
    """
    初始化 selenium
    @return:
    """
    executable_path = "D:\software\install\chromedriver_win32\chromedriver.exe"
    # 设置不弹窗显示
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
    # 弹窗显示
    # browser = webdriver.Chrome(executable_path=executable_path)

    return browser


def craw_info(browser, url):
    """
    爬取数据
    @param browser:
    @param url:
    @return:
    """
    # 拿到网页
    browser.get(url)

    # 输出网页源码
    content = browser.page_source
    soup = BeautifulSoup(content, 'html.parser')
    # 获取中国城市疫情人数
    soup_city_class = soup.find('div', class_='areaBox___Sl7gp themeA___1BO7o').\
        find_all('div', class_='areaBlock2___2gER7')
    list_city_data = []
    for per_city in soup_city_class:
        # 如果存在城市标签，则认为该数据有效，进行解析
        if per_city.find_all('p'):
            # 城市数据
            list_per_city = resolve_info(per_city, 'city')
            list_city_data.append(list_per_city)
    # 数据转换成 DataFrame
    df_city_data = pd.DataFrame(list_city_data, columns=['city', 'curr_diagnose', 'sum_diagnose', 'death', 'cure'])

    # 获取省份疫情人数
    soup_province_class = soup.find('div', class_='areaBox___Sl7gp themeA___1BO7o').\
        find_all('div', class_='areaBlock1___3qjL7')
    list_province_data = []
    for per_province in soup_province_class:
        # 如果存在img标签，则认为该数据有效，进行解析。（否则该数据应该是表头，应跳过）
        if per_province.find_all('p')[0].find('img'):
            # 省份数据
            list_current_province = resolve_info(per_province, 'province')
            list_province_data.append(list_current_province)
    # 数据转换成 DataFrame
    df_province_data = pd.DataFrame(list_province_data, columns=['province', 'curr_diagnose', 'sum_diagnose', 'death', 'cure'])

    browser.quit()
    return df_city_data, df_province_data


def resolve_info(data, tag='city'):
    """
    解析数据
    @param data:
    @param tag:
    @return:
    """
    if tag == 'city':
        # 城市
        data_name = data.find('p', class_='subBlock1___3cWXy').find('span').string
    else:
        # 省份
        data_name = [string for string in data.find('p', class_='subBlock1___3cWXy').strings][0]
    # 现存确诊人数
    data_curr_diagnose = data.find('p', class_='subBlock2___2BONl').string

    if tag == 'city':
        # 累计确诊人数
        data_sum_diagnose = data.find('p', class_='subBlock4___3SAto').string
        # 死亡人数
        data_death = data.find('p', class_='subBlock3___3dTLM').string
    else:
        # 累计确诊人数
        data_sum_diagnose = data.find('p', class_='subBlock3___3dTLM').string
        # 死亡人数
        data_death = data.find('p', class_='subBlock4___3SAto').string

    # 治愈人数
    data_cure = data.find('p', class_='subBlock5___33XVW').string

    return [data_name, data_curr_diagnose, data_sum_diagnose, data_death, data_cure]


if __name__ == '__main__':
    pass