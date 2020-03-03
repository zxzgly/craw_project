# encoding:utf-8
# FileName: main_ncp
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/2/14 11:05
# Description: ncp 爬虫的主函数
import os
import sys
import pandas as pd

'''设置主项目目录，在cmd下执行该脚本不会出现导入其他py文件发生错误'''
sys.path.append(r'D:\code\Python\pycharm-python\d_point\craw_project')
import warnings
warnings.filterwarnings('ignore')

from craw_NCP.plot_data import read_data, plot_map
from craw_NCP.send_email import send_email
from datetime import datetime, timedelta
from craw_NCP.craw_NCP_info import init_selenium, craw_info
from craw_NCP.preprocess_data import process_data, save_to_mysql, compare_data, rename_df

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)

if __name__ == '__main__':
    path_dir = r'D:\note\data_source\ncp_data'
    # 设置昨天的日期作为数据日期
    data_time = datetime.now() + timedelta(-1)
    data_time_str = data_time.strftime('%Y-%m-%d')
    print('程序开始，正在爬取最新疫情数据...')

    """爬虫获取数据"""
    # 丁香园网站
    url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'
    # ①初始化 selenium
    browser = init_selenium()
    # ②获取城市和省份的数据
    df_city_data, df_province_data = craw_info(browser, url)
    print('数据爬取完毕，清洗中...')

    """数据清洗"""
    # ①清洗数据
    df_city_data = process_data(df_city_data, data_time_str, 'city')
    df_province_data = process_data(df_province_data, data_time_str, 'province')
    # 异常数据进行替换
    df_city_data['curr_diagnose'][df_city_data['curr_diagnose'] == '-'] = -1

    # ②保存数据到数据库中
    save_to_mysql(df_city_data, 'city')
    save_to_mysql(df_province_data, 'province')
    print('数据清洗完毕，已保存数据库。数据绘图中...')

    """数据比较并通过 pyecharts 画图"""
    # ①读取数据
    df_city_data, df_province_data = read_data()
    # ②比较数据
    df_city_result, df_plot_city_data = compare_data(df_city_data)
    df_province_result, df_plot_province_data = compare_data(df_province_data)

    # ③各省的热力地图
    filepath_save = os.path.join(path_dir, data_time_str + '_visualmap.png')
    plot_map(df_plot_province_data, '截止' + data_time_str + '中国区当前确认病例分布地图  (by:『知秋小梦』)', filepath_save)
    # ④对列名进行相关更改，方便邮件显示
    df_city_result = rename_df(df_city_result, 'city')
    df_province_result = rename_df(df_province_result, 'province')
    print('地图绘制完毕，邮件发送中...')

    """邮件发送"""
    # ①获取热力地图
    img_list = []
    for filename in os.listdir(path_dir):
        # 获取两天的地图进行比较
        if filename.startswith(data_time_str) or \
                filename.startswith((datetime.now() + timedelta(-2)).strftime('%Y-%m-%d')):
            img_path = os.path.join(path_dir, filename)
            img_list.append(img_path)
    # 发送邮件
    send_email(data_time_str, img_list, df_city_result, df_province_result)
    # 系统退出
    sys.exit(1)
