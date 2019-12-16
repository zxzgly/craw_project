# encoding:utf-8
# FileName: craw_project
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/6 15:50
# Description: 爬取豆瓣top250电影数据
import re
import sys
from collections import OrderedDict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from craw_douban_movie.init_db import connection_to_mysql

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


class DouBanMovie:
    def __init__(self, url, start_page, pages, page_size):
        """
        初始化
        @param url: 爬取主网址
        @param start_page: 起始页码
        @param pages: 总页码（截止页码）
        @param page_size: 每页的大小
        """
        self.url = url
        self.start_page = start_page
        self.pages = pages
        self.page_size = page_size
        self.data_info = []
        self.pymysql_engine, self.pymysql_session = connection_to_mysql()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            # 'Referer': 'https://movie.douban.com/subject/1292052/',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'host':'book.douban.com'
        }

    def get_one_page(self):
        """
        根据起始页码获取当前页面的所有电影
        :return:
        """
        # 如果当前页码小于0，异常退出
        if self.start_page < 0:
            return ""
        # 如果起始页面大于总页码数，退出
        if self.start_page > self.pages:
            return ""

        # 若当前页其实页码小于总页数，继续爬取数据
        while self.start_page<pages:
            # 根据每页数据条数确定起始下标
            start_number = self.start_page * self.page_size
            new_url = self.url + '?start=' + str(start_number) + '&filter='
            print('正在爬取第 {0} 页数据'.format(self.start_page+1))

            # 爬取当前页码的数据
            response = requests.get(url=new_url, headers=self.headers)
            # 解析数据
            self.get_per_movie(response.text)

            # 下一页
            self.start_page = self.start_page + 1

        # 将当前数据保存到数据库中
        self.data_to_mysql()

        return ""

    def get_per_movie(self, one_page_data):
        """
        解析每一页的每一个电影详细链接
        :param one_page_data:
        :return:
        """
        soup = BeautifulSoup(one_page_data, 'html.parser')
        # 定位到每一个电影的 div （pic 标记的 div）
        soup_div_list = soup.find_all(class_="pic")
        # 遍历获取每一个 div 的电影详情链接
        for soup_div in soup_div_list:
            # 定位到每一个电影的 a 标签
            soup_a = soup_div.find_all('a')[0]
            movie_href = soup_a.get('href')
            print(movie_href)
            # 解析数据，获取当前页的 25 个电影详细链接
            self.get_movie_content(movie_href)

        return ""

    def get_movie_content(self, movie_detail_href):
        """
        解析影片详细内容
        @param movie_detail_href:
        @return:
        """

        '''获取评论数据：备用'''
        # # 解析网址，获得唯一标签数字
        # number = re.findall(r'\d+', 'https://movie.douban.com/subject/1292052/')[0]
        # # 组成新的 url， 并获取返回的 json 数据
        # json_url = 'https://m.douban.com/rexxar/api/v2/gallery/subject_feed?start=0&count=4&subject_id=' + number + '&ck=null'
        #
        # json_headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        #     'Referer': 'https://movie.douban.com/subject/1292052/',
        # }
        # # 设置 header 的 Referer即可爬取到 json 数据
        # response = requests.get(url=json_url, headers=json_headers)
        # data_json = response.json()

        # 生成一个有序字典，保存影片结果
        movie_info = OrderedDict()
        '''爬取页面，获得详细数据'''
        response = requests.get(url=movie_detail_href, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析电影排名和名称
        movie_info['movie_rank'] = soup.find_all('span', class_='top250-no')[0].string
        movie_info['movie_name'] = soup.find_all('span', property='v:itemreviewed')[0].string

        # 定位到影片数据的 div
        soup_div = soup.find(id='info')
        # 解析电影发布信息
        movie_info['movie_director'] = self.get_mul_tag_info(soup_div.find_all('span')[0].find_all('a'))
        movie_info['movie_writer'] = self.get_mul_tag_info(soup_div.find_all('span')[3].find_all('a'))
        movie_info['movie_starring'] = self.get_mul_tag_info(soup_div.find_all('span')[6].find_all('a'))
        movie_info['movie_type'] = self.get_mul_tag_info(soup_div.find_all('span', property='v:genre'))
        movie_info['movie_country'] = soup_div.find(text='制片国家/地区:').next_element.lstrip().rstrip()
        movie_info['movie_language'] = soup_div.find(text='语言:').next_element.lstrip().rstrip()
        movie_info['movie_release_date'] = self.get_mul_tag_info(soup_div.find_all('span', property='v:initialReleaseDate'))
        movie_info['movie_run_time'] = self.get_mul_tag_info(soup_div.find_all('span', property='v:runtime'))
        movie_info['movie_imdb_href'] = soup_div.find('a', target='_blank')['href']

        movie_second_name = ''
        try:
            movie_second_name = soup_div.find(text='又名:').next_element.lstrip().rstrip()
        except AttributeError:
            print('{0} 没有又名'.format(movie_info['movie_name']))
            movie_info['movie_second_name'] = movie_second_name

        # 获取总评分和总评价人数
        movie_info['movie_rating'] = soup.find_all('strong', property='v:average')[0].string
        movie_info['movie_comments_user'] = soup.find_all('span', property='v:votes')[0].string
        # 定位到影片星级评分占比的 div
        soup_div = soup.find('div', class_="ratings-on-weight")
        # 获取每个星级的评分
        movie_info['movie_five_star_ratio'] = soup_div.find_all('div')[0].find(class_='rating_per').string
        movie_info['movie_four_star_ratio'] = soup_div.find_all('div')[2].find(class_='rating_per').string
        movie_info['movie_three_star_ratio'] = soup_div.find_all('div')[4].find(class_='rating_per').string
        movie_info['movie_two_star_ratio'] = soup_div.find_all('div')[6].find(class_='rating_per').string
        movie_info['movie_one_star_ratio'] = soup_div.find_all('div')[8].find(class_='rating_per').string
        movie_info['movie_note'] = ''

        print(movie_info)
        exit()
        # 保存当前影片信息
        self.data_info.append(movie_info)

    def data_to_mysql(self):
        """
        保存数据到数据库中
        @return:
        """
        # 获取数据并保存成 DataFrame
        df_data = pd.DataFrame(self.data_info)
        df_data.to_csv(r'C:\Users\wzg\Desktop\data_movie.csv', encoding='utf-8', index=False)
        # 导入数据到 mysql 中
        df_data.to_sql('t_douban_movie_top_250', self.pymysql_engine, index=False, if_exists='append')

    def get_mul_tag_info(self, soup_span):
        """
        获取多个标签的结果合并在一个结果中返回，并用 / 分割
        :param soup_span:
        :type soup_span:
        :return:
        :rtype:
        """
        info = ''
        for second_span in soup_span:
            # 区分 href 和标签内容
            info = ('' if (info == '') else '/').join((info, second_span.string))

        return info


if __name__ == '__main__':
    url = 'https://movie.douban.com/top250'
    start_page = 0
    pages = 10
    page_size = 25
    douban_movie = DouBanMovie(url, start_page, pages, page_size)
    douban_movie.get_one_page()

    # # 获取数据并保存成 DataFrame
    # df_data = pd.read_csv(r'C:\Users\wzg\Desktop\data_movie.csv', encoding='utf-8')
    # # df_data.to_csv(r'C:\Users\wzg\Desktop\data_movie.csv', encoding='utf-8', index=False)
    # # 导入数据到 mysql 中
    # print(df_data)
    # pymysql_engine, pymysql_session = connection_to_mysql()
    # df_data.to_sql('t_douban_movie_top_250', pymysql_engine, index=False, if_exists='append')

