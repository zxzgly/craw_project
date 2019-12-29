# encoding:utf-8
# FileName: craw_lianjia_house
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/25 18:52
# Description: 爬取链接网的租房信息
import os
import random
import re
import time
from collections import OrderedDict
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from craw_lianjia.init_db import connection_to_mysql


class LianJiaHouse:
    def __init__(self, city, url, page_size, save_file_path):
        """
        初始化
        @param url: 主起始页
        @param page_size: 每一页的出租房屋个数
        """
        # 城市
        self.city = city
        # 主起始页
        self.base_url = url
        # 当前筛选条件下的页面
        self.current_url = url
        # 行政区域
        self.area = []
        # 出租方式：整租+合租
        self.rental_method = ['rt200600000001', 'rt200600000002']
        # 户型：一居、二居、三居、四居+
        self.rooms_number = ['l0', 'l1', 'l2', 'l3']
        # 房间面积：<=40平米、40-60、60-80、80-100、100-120、>120
        # self.room_size = ['ra0', 'ra1', 'ra2', 'ra3', 'ra4', 'ra5']
        # 其实页码默认为0
        self.start_page = 0
        # 当前条件下的总数据页数
        self.pages = 0
        # 每一页的出租房屋个数
        self.page_size = page_size
        # 最大页数
        self.max_pages = 100
        # 设置最大数据量，测试用
        self.count = 0
        # 本地文件保存地址
        self.save_file_path = save_file_path
        # 所有已经保存的房屋 id，用来验证去重
        self.house_id = self.get_exists_house_id()
        # 保存数据
        self.data_info = []
        # 系统等待时间：最大时间 + 最小时间（单位：秒）
        self.await_max_time = 8
        self.await_min_time = 2
        # 重连次数
        self.retry = 5
        # 爬取时间较长，所以在保存数据的时候进行数据库连接，不在此进行数据库连接
        self.pymysql_engine, self.pymysql_session = None, None
        # 设置爬虫头部，建议多设置一些，防止被封
        self.headers = {
            'User-Agent': self.get_ua(),
        }

    def get_main_page(self):
        """
        进入主起始页
        @return:
        """
        # 获取当前筛选条件下数据总条数
        soup, count_main = self.get_house_count()

        # 如果当前当前筛选条件下的数据个数大于最大可查询个数，则设置第一次查询条件
        if int(count_main) > self.page_size*self.max_pages:
            # 获取当前地市的所有行政区域，当做第一个查询条件
            soup_uls = soup.find_all('li', class_='filter__item--level2', attrs={'data-type': 'district'})
            self.area = self.get_area_list(soup_uls)

            # 遍历行政区域，重新生成筛选条件
            for area in self.area:
                self.get_area_page(area)
        else:
            # 直接获取数据
            self.get_pages(int(count_main), '', '', '')

        # 保存数据到数据库中
        self.data_to_sql()

    def get_area_page(self, area):
        """
        当前搜索条件：行政区域
        @param area:
        @return:
        """
        # 重新拼接行政区域访问的 url
        self.current_url = self.base_url + area + '/'
        # 获取当前筛选条件下数据总条数
        soup, count_area = self.get_house_count()

        '''如果当前当前筛选条件下的数据个数大于最大可查询个数，则设置第二次查询条件'''
        if int(count_area) > self.page_size * self.max_pages:
            # 遍历出租方式，重新生成筛选条件
            for rental_method in self.rental_method:
                self.get_area_and_rental_page(area, rental_method)
        else:
            print('当前筛选条件：{0}， 共 {1} 条数据，正在获取第 {2} 页'.format(area, count_area, self.pages))
            self.get_pages(int(count_area), area, '', '')

    def get_area_and_rental_page(self, area, rental_method):
        """
        当前搜索条件：行政区域 + 出租方式
        @param area: 行政区域
        @param rental_method: 出租方式
        @return:
        """
        # 重新拼接行政区域 + 出租方式访问的 url
        self.current_url = self.base_url + area + '/' + rental_method + '/'
        # 获取当前筛选条件下数据总条数
        soup, count_area_rental = self.get_house_count()

        '''如果当前当前筛选条件下的数据个数大于最大可查询个数，则设置第三次查询条件'''
        if int(count_area_rental) > self.page_size * self.max_pages:
            # 遍历房屋户型，重新生成筛选条件
            for room_number in self.rooms_number:
                self.get_area_and_rental_and_room_page(area, rental_method, room_number)
        else:
            print('当前搜索条件：{0} {1}， 共 {2} 条数据，正在获取第 {3} 页'.format(
                area, rental_method, count_area_rental, self.pages))
            self.get_pages(int(count_area_rental), area, rental_method, '')

    def get_area_and_rental_and_room_page(self, area, rental_method, room_number):
        """
        当前搜索条件：行政区域 + 出租方式 + 居室数
        @param area: 行政区域
        @param rental_method: 出租方式
        @param room_number: 居室数
        @return:
        """
        # 重新拼接行政区域 + 出租方式访问的 url
        self.current_url = self.base_url + area + '/' + rental_method + room_number + '/'
        # 获取当前筛选条件下数据总条数
        soup, count_area_rental_room = self.get_house_count()

        '''如果当前当前筛选条件下的数据个数大于最大可查询个数，则设置第三次查询条件'''
        if int(count_area_rental_room) > self.page_size * self.max_pages:
            print('==================无法获取所有数据，当前筛选条件数据个数超过总数，将爬取前100页数据')
            # send_email()
            print('当前搜索条件：{0} {1} {2}， 共 {3} 条数据，正在获取第 {4} 页'.format(
                area, rental_method, room_number, count_area_rental_room, self.pages))
            self.get_pages(int(self.page_size * self.max_pages), area, rental_method, room_number)

        else:
            print('当前搜索条件：{0} {1} {2}， 共 {3} 条数据，正在获取第 {4} 页'.format(
                area, rental_method, room_number, count_area_rental_room, self.pages))
            self.get_pages(int(count_area_rental_room), area, rental_method, room_number)

    def get_pages(self, count_number, area, rental_method, room_number):
        """
        根据查询到的页面总数据，确定分页
        @param count_number: 总数据量
        @param area: 区域
        @param rental_method: 出租方式
        @param room_number:居室数
        @return:
        """
        # 确定页数
        self.pages = int(count_number/self.page_size) \
            if (count_number%self.page_size) == 0 else int(count_number/self.page_size)+1

        '''遍历每一页'''
        for page_index in range(1, self.pages+1):
            self.current_url = self.base_url + area + '/' + 'pg' + str(page_index) + rental_method + room_number + '/'

            # 解析当前页的房屋信息，获取到每一个房屋的详细链接
            self.get_per_house()
            page_index += 1

    def get_per_house(self):
        """
        解析每一页中的每一个房屋的详细链接
        @return:
        """
        print(self.current_url)
        # 爬取当前页码的数据
        response = requests.get(url=self.current_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 定位到每一个房屋的 div （pic 标记的 div）
        soup_div_list = soup.find_all(class_='content__list--item--main')
        # 遍历获取每一个 div 的房屋详情链接和房屋地址
        for soup_div in soup_div_list:
            # 定位并获取每一个房屋的详情链接
            detail_info = soup_div.find_all('p', class_='content__list--item--title twoline')[0].a.get('href')
            detail_href = 'https://sz.lianjia.com/' + detail_info

            # 获取详细链接的编号作为房屋唯一id
            house_id = detail_info.split('/')[2].replace('.html', '')
            '''解析部分数据'''
            # 获取该页面中房屋的地址信息和其他详细信息
            detail_text = soup_div.find_all('p', class_='content__list--item--des')[0].get_text()
            info_list = detail_text.replace('\n', '').replace(' ', '').split('/')
            # 获取房屋租金数据
            price_text = soup_div.find_all('span', class_='content__list--item-price')[0].get_text()

            # 如果地址信息为空，可以确定是公寓，而我们并不能在公寓详情界面拿到数据，所以，丢掉
            if len(info_list) == 5:
                # 如果当前房屋信息已经爬取过
                if self.check_exist(house_id):
                    print('房屋id：{0} 已经保存，不再重复爬取！'.format(house_id))
                else:
                    # 解析当前房屋的详细数据
                    self.get_house_content(detail_href, house_id, info_list, price_text)

        return ""

    def get_house_content(self, href, house_id, info_list, price_text):
        """
        获取房屋详细信息页面的内容
        @param href: 详细页面链接
        @param house_id: 上个页面传递的房租id
        @param info_list: 上个页面传递的部分数据
        @param price_text: 上个页面传递的房租数据
        @return:
        """
        # 每1000条记录需要自行决定是否要继续
        if int(self.count/1000) > 0:
            input_text = input("================> 是否退出？输入Q/q直接退出：")

            if input_text == "Q" or input_text == "q":
                # 保存数据到数据库中
                self.data_to_sql()
                print("==================数据已保存数据库，程序已退出！==================")
                exit(0)
            else:
                print("==================> 继续爬取数据中...")
                self.count = 0

        # 生成一个有序字典，保存房屋结果
        house_info = OrderedDict()
        for i in range(0, self.retry):
            try:
                # 随机休眠3-8 秒
                time.sleep(random.randint(self.await_min_time, self.await_max_time))

                '''爬取页面，获得详细数据'''
                response = requests.get(url=href, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                '''获取上一个页面传递的房屋数据'''
                house_info['house_address'] = info_list[0]
                house_info['house_rental_area'] = info_list[1]
                house_info['house_orientation'] = info_list[2]
                house_info['house_layout'] = info_list[3]
                house_info['house_floor'] = info_list[4]
                house_info['house_rental_price'] = price_text

                '''解析房源维护时间'''
                soup_div_text = soup.find_all('div', class_='content__subtitle')[0].get_text()
                house_info['house_id'] = house_id   # 房源编号数据直接从上个页面获取
                # house_info['house_id'] = re.findall(r'[A-Z]*\d{5,}', soup_div_text)[0]
                house_info['house_update_time'] = re.findall(r'\d{4}-\d{2}-\d{2}', soup_div_text)[0]

                '''解析经纬度数据'''
                # 获取到经纬度的 script定义数据
                location_str = response.text[re.search(r'(g_conf.coord)+', response.text).span()[0]:
                                             re.search(r'(g_conf.subway)+', response.text).span()[0]]
                # 字符串清洗，并在键上添加引号，方便转化成字典
                location_str = location_str.replace('\n', '').replace(' ', '').replace("longitude", "'longitude'").\
                    replace("latitude", "'latitude'")
                # 获取完整经纬度数据，转换成字典，并保存
                location_dict = eval(location_str[location_str.index('{'): location_str.index('}')+1])
                house_info['house_longitude'] = location_dict['longitude']
                house_info['house_latitude'] = location_dict['latitude']

                '''解析房屋出租方式（整租/合租/不限）'''
                house_info['house_rental_method'] = soup.find_all('ul', class_='content__aside__list')[0].find_all('li')[0].\
                    get_text().replace('租赁方式：', '')

                '''解析房屋的标签'''
                house_info['house_tag'] = soup.find_all('p', class_='content__aside--tags')[0].\
                    get_text().replace('\n', '/').replace(' ', '')

                '''房屋其他基本信息'''
                # 定位到当前div并获取所有基本信息的 li 标签
                soup_li = soup.find_all('div', class_='content__article__info', attrs={'id': 'info'})[0]. \
                    find_all('ul')[0].find_all('li', class_='fl oneline')
                # 赋值房屋信息
                house_info['house_elevator'] = soup_li[8].get_text().replace('电梯：', '')
                house_info['house_parking'] = soup_li[10].get_text().replace('车位：', '')
                house_info['house_water'] = soup_li[11].get_text().replace('用水：', '')
                house_info['house_electricity'] = soup_li[13].get_text().replace('用电：', '')
                house_info['house_gas'] = soup_li[14].get_text().replace('燃气：', '')
                house_info['house_heating'] = soup_li[16].get_text().replace('采暖：', '')
                house_info['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                house_info['city'] = self.city

                print(house_info['house_address'])
                # 保存当前影片信息
                self.data_info.append(house_info)
                self.count += 1

                '''超过10条数据，保存到本地'''
                if len(self.data_info) >= 50:
                    self.data_to_csv()
                # 处理无异常在，跳出循环，否则，进行重试
                break
            except Exception as e:
                print(e)
                print('爬取数据异常，重新尝试爬取数据。爬取地址：{0}'.format(href))

    def check_exist(self, house_id):
        """
        检查当前要获取的房屋数据是否已经存在
        @param house_id:
        @return:
        """
        # 通过检查当前数据中 房屋id 是否存在
        if house_id in self.house_id:
            return True
        else:
            self.house_id.append(house_id)
            return False

    def get_exists_house_id(self):
        """
        通过已经爬取到的房屋信息，并获取房屋id
        @return:
        """
        if os.path.exists(self.save_file_path):
            df_data = pd.read_csv(self.save_file_path, encoding='utf-8', )
            return df_data['house_id'].to_list()
        else:
            return []

    def data_to_sql(self):
        """
        保存/追加数据到数据库中
        @return:
        """
        # 连接数据库
        self.pymysql_engine, self.pymysql_session = connection_to_mysql()
        # 读取数据并保存到数据库中
        df_data = pd.read_csv(self.save_file_path, encoding='utf-8')
        # 导入数据到 mysql 中
        df_data.to_sql('t_lianjia_rent_info', self.pymysql_engine, index=False, if_exists='append')

    def data_to_csv(self):
        """
        保存/追加数据到本地
        @return:
        """
        # 获取数据并保存成 DataFrame
        df_data = pd.DataFrame(self.data_info)

        if os.path.exists(self.save_file_path) and os.path.getsize(self.save_file_path):
            # 追加写入文件
            df_data.to_csv(self.save_file_path, mode='a', encoding='utf-8', header=False, index=False)
        else:
            # 写入文件，带表头
            df_data.to_csv(self.save_file_path, mode='a', encoding='utf-8', index=False)

        # 清空当前 数据集
        self.data_info = []

    def get_house_count(self):
        """
        获取当前筛选条件下的房屋数据个数
        @param text:
        @return:
        """
        # 爬取区域起始页面的数据
        response = requests.get(url=self.current_url, headers=self.headers)
        # 通过 BeautifulSoup 进行页面解析
        soup = BeautifulSoup(response.text, 'html.parser')
        # 获取数据总条数
        count = soup.find_all(class_='content__title--hl')[0].string

        return soup, count

    def get_area_list(self, soup_uls):
        """
        获取地市的所有行政区域信息，并保存
        @param soup_uls:
        @return:
        """
        area_list = []
        for soup_ul in soup_uls:
            # 获取 ul 中的 a 标签的 href 信息中的区域属性
            href = soup_ul.a.get('href')
            # 跳过第一条数据
            if href.endswith('/zufang/'):
                continue
            else:
                # 获取区域数据，保存到列表中
                area_list.append(href.replace('/zufang/', '').replace('/', ''))

        return area_list

    def get_ua(self):
        """
        在UA库中随机选择一个UA
        :return: 返回一个库中的随机UA
        """
        ua_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Opera/8.0 (Windows NT 5.1; U; en)",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Macintosh; U; IntelMac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

        return random.choice(ua_list)


if __name__ == '__main__':
    city_number = 'sz'
    city_name = '深圳'
    url = 'https://{0}.lianjia.com/zufang/'.format(city_number)
    page_size = 30
    save_file_path = r'C:\Users\wzg\Desktop\data_house.csv'
    lianjia_house = LianJiaHouse(city_name, url, page_size, save_file_path)
    lianjia_house.get_main_page()