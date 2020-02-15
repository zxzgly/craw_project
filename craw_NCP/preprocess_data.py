# encoding:utf-8
# FileName: preprocess_data
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/2/13 17:01
# Description: 爬取的数据预处理 + 画图的数据预处理
import numpy as np
from sqlalchemy import create_engine


def process_data(df_data, time_str, tag='city'):
    """
    对爬取的数据进行清洗处理
    @param df_data:
    @param time_str:
    @param tag:
    @return:
    """
    # 删除地市的不明确数据
    if tag == 'city':
        df_data.drop(index=df_data[df_data['city'] == '待明确地区'].index, axis=1, inplace=True)
        # df_data.drop(df_data['city'] == '外地来京人员', axis=1, inplace=True)
        # df_data.drop(df_data['city'] == '外地来沪人员', axis=1, inplace=True)
        # df_data.drop(df_data['city'] == '外地来津人员', axis=1, inplace=True)

    # 填充空记录为0
    df_data.fillna(0, inplace=True)
    # 增加日期字段
    df_data['date'] = time_str
    return df_data


def save_to_mysql(df_data, tag='city'):
    """
    保存数据到数据库中
    @param df_data:
    @param tag:
    @return:
    """
    # 连接数据库
    connect = create_engine('mysql+pymysql://username:password@localhost:3306/dbname?charset=utf8')

    # 设置要保存的数据库表
    if tag == 'city':
        table_name = 't_ncp_city_info'
    else:
        table_name = 't_ncp_province_info'
    # 保存数据到数据库中
    df_data.to_sql(name=table_name, con=connect, index=False, if_exists='append')


def rename_df(df_data, tag='city'):
    """
    对列名进行处理
    @param df_data:
    @param tag:
    @return:
    """
    if tag == 'city':
        name = '城市'
    else:
        name = '省份'

    df_data = df_data[[tag, 'sum_diagnose', 'sum_diagnose_nc', 'sum_diagnose_ratio',
                       'curr_diagnose', 'curr_diagnose_nc', 'curr_diagnose_ratio',
                       'death', 'death_nc', 'death_ratio',
                       'cure', 'cure_nc', 'cure_ratio']]

    df_data.rename(
        columns={
            tag: name,
            'sum_diagnose': '累计确诊人数',
            'sum_diagnose_nc': '新增累积确诊人数',
            'sum_diagnose_ratio': '累计确诊环比增长率',
            'curr_diagnose': '现存确诊人数',
            'curr_diagnose_nc': '新增现存确诊人数',
            'curr_diagnose_ratio': '现存确诊环比增长率',
            'death': '死亡人数',
            'death_nc': '新增死亡人数',
            'death_ratio': '死亡环比增长率',
            'cure': '治愈人数',
            'cure_nc': '新增治愈人数',
            'cure_ratio': '治愈环比增长率'
        }, inplace=True
    )

    # 数据排序
    df_data.sort_values(['累计确诊人数', '新增累积确诊人数'], inplace=True, ascending=False)
    df_data = df_data.reset_index(drop=True)

    return df_data


def compare_data(df_data):
    """
    比较最新的两天数据做差
    @param df_data:
    @param tag:
    @return:
    """
    # 获取数据日期
    date_list = df_data['date'].drop_duplicates().values.tolist()
    # 去除id列
    df_data.drop('id', axis=1, inplace=True)
    # 根据日期拆分dataframe
    df_data_1 = df_data[df_data['date'] == date_list[0]]
    df_data_2 = df_data[df_data['date'] == date_list[1]]
    # 重置索引列
    df_data_1 = df_data_1.reset_index(drop=True)
    df_data_2 = df_data_2.reset_index(drop=True)

    if date_list[1] < date_list[0]:
        temp = df_data_1
        df_data_1 = df_data_2
        df_data_2 = temp
    # 昨天-前天 比较新增数据
    df_data_2['curr_diagnose_nc'] = df_data_2['curr_diagnose'] - df_data_1['curr_diagnose']
    df_data_2['sum_diagnose_nc'] = df_data_2['sum_diagnose'] - df_data_1['sum_diagnose']
    df_data_2['death_nc'] = df_data_2['death'] - df_data_1['death']
    df_data_2['cure_nc'] = df_data_2['cure'] - df_data_1['cure']
    # 新增较上一日环比列
    df_data_2['curr_diagnose_ratio'] = (df_data_2['curr_diagnose_nc'] / df_data_1['curr_diagnose']).apply(
        lambda x: format(x, '.2%'))
    df_data_2['sum_diagnose_ratio'] = (df_data_2['sum_diagnose_nc'] / df_data_1['sum_diagnose']).apply(
        lambda x: format(x, '.2%'))
    df_data_2['death_ratio'] = (df_data_2['death_nc'] / df_data_1['death']).apply(lambda x: format(x, '.2%'))
    df_data_2['cure_ratio'] = (df_data_2['cure_nc'] / df_data_1['cure']).apply(lambda x: format(x, '.2%'))

    # 对新增城市的数据进行填充
    df_data_2.fillna(0, inplace=True)
    df_data_2[['curr_diagnose_nc', 'sum_diagnose_nc', 'death_nc', 'cure_nc']] = \
        df_data_2[['curr_diagnose_nc', 'sum_diagnose_nc', 'death_nc', 'cure_nc']].astype(int)

    return df_data_2


if __name__ == '__main__':
    pass

