# encoding:utf-8
# FileName: data_plot
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/2/13 19:52
# Description: 通过数据进行绘图展示
from datetime import datetime, timedelta
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from sqlalchemy import create_engine


def read_data():
    """
    获取前两天的数据
    @return:
    """
    # 设置昨天的日期作为数据日期
    data_time = datetime.now() + timedelta(-2)
    data_time_str = data_time.strftime('%Y-%m-%d')

    # 连接数据库
    connect = create_engine('mysql+pymysql://username:password@localhost:3306/dbname?charset=utf8')

    # 获取前两天的数据
    sql_city = 'select * from t_ncp_city_info where date>="{0}"'.format(data_time_str)
    df_city_data = pd.read_sql_query(sql_city, connect)
    sql_province = 'select * from t_ncp_province_info where date>="{0}"'.format(data_time_str)
    df_province_data = pd.read_sql_query(sql_province, connect)

    return df_city_data, df_province_data


def plot_map(df_data, title, filepath_save):
    """
    绘制地图
    @param df_data:
    @param filepath_save:
    @return:
    """
    # 获取数据
    list_data = df_data.iloc[:, [1, 3]].values.tolist()
    # 绘制地图
    ncp_map = (
        Map(init_opts=opts.InitOpts('1000px', '600px'))
        .add('', list_data, 'china')
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                pos_left='center'
            ),
            visualmap_opts=opts.VisualMapOpts(
                # 设置为分段形数据显示
                is_piecewise=True,
                # 设置拖拽用的手柄
                is_calculable=True,
                # 设置数据最大值
                max_=df_data['sum_diagnose'].max(),
                # 自定义的每一段的范围，以及每一段的文字，以及每一段的特别的样式。
                pieces=[
                    {'min': 10001, 'label': '>10000', 'color': '#4F040A'},
                    {'min': 1000, 'max': 10000, 'label': '1000 - 10000', 'color': '#811C24'},
                    {'min': 500, 'max': 999, 'label': '500 - 999', 'color': '#CB2A2F'},
                    {'min': 100, 'max': 499, 'label': '100 - 499', 'color': '#E55A4E'},
                    {'min': 10, 'max': 99, 'label': '10 - 99', 'color': '#F59E83'},
                    {'min': 1, 'max': 9, 'label': '1 - 9', 'color': '#FDEBCF'},
                    {'min': 0, 'max': 0, 'label': '0', 'color': '#F7F7F7'}
                ]
            ),
        )
    )
    # 保存图片到本地
    make_snapshot(snapshot, ncp_map.render(), filepath_save)


if __name__ == '__main__':
    pass