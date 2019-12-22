# encoding:utf-8
# FileName: douban_moive_analysis
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/14 18:43
# Description: 豆瓣top250电影分析
import re
from collections import Counter

import numpy as np
import pandas as pd

from craw_douban.init_db import connection_to_mysql
import matplotlib.pyplot as plt
import seaborn as sns

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置可以一行显示
# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)


def sns_set():
    """
    sns 相关设置
    @return:
    """
    # 声明使用 Seaborn 样式
    sns.set()
    # 有五种seaborn的绘图风格，它们分别是：darkgrid, whitegrid, dark, white, ticks。默认的主题是darkgrid。
    sns.set_style("whitegrid")
    # 有四个预置的环境，按大小从小到大排列分别为：paper, notebook, talk, poster。其中，notebook是默认的。
    sns.set_context('talk')
    # 中文字体设置-黑体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决保存图像是负号'-'显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False
    # 解决Seaborn中文显示问题并调整字体大小
    sns.set(font='SimHei')

    return sns


def read_data():
    """
    读取数据库中的数据
    @return:
    """
    # 建立数据库连接
    engine, db_session = connection_to_mysql()
    # 写一条sql
    sql = 'select * from t_douban_movie_top_250'
    # 获取数据库中的所有数据
    data = pd.read_sql(sql, con=engine)

    return data


def reshape_data(df_data):
    """
    针对每个数据字段进行清洗
    @param df_data:
    @return:
    """

    ''' 1. 查看整体数据类型与缺失情况'''
    print(df_data.info())
    ''' 
    id                        250 non-null int64
    movie_rank                250 non-null object
    movie_name                250 non-null object
    movie_director            250 non-null object
    movie_writer              250 non-null object
    movie_starring            250 non-null object
    movie_type                250 non-null object
    movie_country             250 non-null object
    movie_language            250 non-null object
    movie_release_date        250 non-null object
    movie_run_time            250 non-null object
    movie_second_name         2 non-null object
    movie_imdb_href           250 non-null object
    movie_rating              250 non-null object
    movie_comments_user       250 non-null object
    movie_five_star_ratio     250 non-null object
    movie_four_star_ratio     250 non-null object
    movie_three_star_ratio    250 non-null object
    movie_two_star_ratio      250 non-null object
    movie_one_star_ratio      250 non-null object
    movie_note                250 non-null object
    影片又名信息有两个为空，其他数据均不为空
    '''
    # 对于部分影片缺失又名信息，用影片名称去填充即可
    df_data['movie_second_name'].fillna(df_data['movie_name'], inplace=True)
    print(df_data.info())

    ''' 2. 查看单个指标的数据，并进行相应的清洗操作'''
    # 1. 影片排名数据，可以看到数据形式是 No.XX 类型，若是建模的话，这种数据类型是不符合要求
    print(df_data['movie_rank'].head(5))
    # 这里我们将 No.XX 数据的 No. 删掉，只保留后面的数字即可
    df_data['movie_rank'] = df_data['movie_rank'].str.replace('No.', '').astype(int)

    # 2. 影片类型，可以看到数据形式是 xx/xx/xx 的形式，数据规整，不需要处理，若是建模的话可以对其进行独热编码
    print(df_data['movie_type'].head(5))

    # 3. 影片制作国家，可以看到数据形式是 xx / xx 的形式， 用 / 分割，数据规整，但需要对空格进行处理
    print(df_data['movie_country'].head(10))
    # 这里直接去空格进行替换
    df_data['movie_country'] = df_data['movie_country'].str.replace(' ', '')

    # 4. 影片语言，同影片制作国家的数据类型一致，可同等处理
    print(df_data['movie_language'].head(10))
    df_data['movie_language'] = df_data['movie_language'].str.replace(' ', '')

    # 5. 影片上映日期，可以看到部分影片存在多个上映日期和上映城市
    print(df_data['movie_release_date'].head(10))
    # 这里直接只保留第一次上映城市的日期，并新增一列上映城市，日期保留年份即可
    df_data['movie_release_date'] = df_data['movie_release_date'].apply(lambda e: re.split(r'/', e)[0])
    df_data['movie_release_city'] = df_data['movie_release_date'].apply(lambda e: e[11:-1])
    df_data['movie_release_date'] = df_data['movie_release_date'].apply(lambda e: e[:4])

    # 6. 影片片长，可以看到影片片长为 XX分钟 这种形式，还有部分是 110分钟(剧场版)这种形式
    print(df_data['movie_run_time'].head(10))
    # 这里直接保留影片分钟数
    df_data['movie_run_time'] = df_data['movie_run_time'].apply(lambda e: re.findall(r'\d+', e)[0]).astype(int)

    # 7. 影片总评分，影片评论数，设置为相应的数据格式即可
    print(df_data[['movie_rating', 'movie_comments_user']].head(10))
    # 这里将影片总评分转换为 float、影评人数转换为 int（默认都是 object类型）
    df_data['movie_rating'] = df_data['movie_rating'].astype(float)
    df_data['movie_comments_user'] = df_data['movie_comments_user'].astype(int)

    # 8. 影片星级评分占比，可以看出占比为 xx% 的形式
    print(df_data[['movie_five_star_ratio', 'movie_four_star_ratio', 'movie_three_star_ratio',
                   'movie_two_star_ratio', 'movie_one_star_ratio']].head(10))
    # 这里对所有星级的影片进行处理，保留占比数字
    df_data['movie_five_star_ratio'] = df_data['movie_five_star_ratio'].str.strip('%').astype(float) / 100
    df_data['movie_four_star_ratio'] = df_data['movie_four_star_ratio'].str.strip('%').astype(float) / 100
    df_data['movie_three_star_ratio'] = df_data['movie_three_star_ratio'].str.strip('%').astype(float) / 100
    df_data['movie_two_star_ratio'] = df_data['movie_two_star_ratio'].str.strip('%').astype(float) / 100
    df_data['movie_one_star_ratio'] = df_data['movie_one_star_ratio'].str.strip('%').astype(float) / 100

    # 影片名称、影片导演、影片编剧、影片主演、影片又名、影片IMDb 链接、影片备注信息暂时不需要进行处理，保持即可

    return df_data


def view_data(df_data):
    """
    可视化分析
    @param data:
    @return:
    """
    # 声明使用 Seaborn 样式
    sns = sns_set()

    '''1. 数据认识与探索'''
    print(df_data.info())

    '''1.1. 数据异常值等分析'''
    # 由于本次数据为规整数据，无异常值数据，可以不用处理

    '''1.2. 对数值型特征进行简单的描述性统计，包括均值，中位数，众数，方差，标准差，最大值，最小值等'''
    print(df_data.describe())
    # 通过描述性统计结果客粗略的判断存在着异常值的特征

    '''1.3. 判断这些特征都是什么数据类型？定类？定序？定距？还是定比？'''
    # 提示：弄清楚这一步主要是为了后续正确找对方法进行可视化
    '''
    影片类型、影片制片国家、影片语言: 定类数据
    影片片长、影片总评分、影片评论数、影片时间：定距数据
    影片5/4/3/2/1星占比：定比数据
    '''

    '''2. 数据可视化探索'''
    '''
    提示：根据上面自己对各个特征数据类型的判断，选择合适的可视化方法完成可视化。
    '''

    '''2.1 定类/定序特征分析'''
    '''2.1.1 将影片类型数据通过 / 分割后统计每个类型出现的次数'''
    df_data['movie_type_arr'] = df_data['movie_type'].map(lambda e: e.split('/'))
    # 将数据转换成一维数组
    movie_type_list = np.concatenate(df_data['movie_type_arr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个类型的个数
    movie_type_counter = pd.DataFrame(movie_type_list, columns=['movie_type'])['movie_type'].value_counts()
    # 生成柱状图的数据 x 和 y
    movie_type_x = movie_type_counter.index.tolist()
    movie_type_y = movie_type_counter.values.tolist()

    # 画出影片类型的柱状图
    ax1 = sns.barplot(x=movie_type_x, y=movie_type_y, palette="Blues_r", )
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax1.set_title('豆瓣影片Top250类型统计    by:『知秋小梦』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax1.set_xlabel('影片类型', fontsize=10)
    ax1.set_ylabel('类型出现次数', fontsize=10)
    # 设置坐标轴刻度的字体大小
    ax1.tick_params(axis='x', labelsize=8)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_type_x)), movie_type_y):
        ax1.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()

    ''''2.1.2 同理将影片语言数据通过 / 分割后统计每个语言出现的次数'''
    df_data['movie_language_arr'] = df_data['movie_language'].map(lambda e: e.split('/'))
    # 将数据转换成一维数组
    movie_language_list = np.concatenate(df_data['movie_language_arr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个语言的个数
    movie_language_counter = pd.DataFrame(movie_language_list, columns=['movie_language'])['movie_language'].value_counts()
    # 生成柱状图的数据 x 和 y
    movie_language_x = movie_language_counter.index.tolist()
    movie_language_y = movie_language_counter.values.tolist()

    # 画出影片语言分布的柱状图
    ax2 = sns.barplot(x=movie_language_x, y=movie_language_y, palette="Blues_r",)
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax2.set_title('豆瓣影片Top250语言统计    by:『知秋小梦』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax2.set_xlabel('影片语言', fontsize=10)
    # 设置 x 轴标签文字的方向
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=-90)
    ax2.set_ylabel('语言出现次数', fontsize=10)
    # 设置坐标轴刻度的字体大小
    ax2.tick_params(axis='x', labelsize=8)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_language_x)), movie_language_y):
        ax2.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()

    ''''2.1.3 同理将影片制片国家/地区数据通过 / 分割后统计每个国家/地区出现的次数'''
    df_data['movie_country_arr'] = df_data['movie_country'].map(lambda e: e.split('/'))
    # 将数据转换成一维数组
    movie_country_list = np.concatenate(df_data['movie_country_arr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个国家/地区的个数
    movie_country_counter = pd.DataFrame(movie_country_list, columns=['movie_country'])[
        'movie_country'].value_counts()
    # 生成柱状图的数据 x 和 y
    movie_country_x = movie_country_counter.index.tolist()
    movie_country_y = movie_country_counter.values.tolist()

    # 画出影片制片国家/地区分布的柱状图
    ax3 = sns.barplot(x=movie_country_x, y=movie_country_y, palette="Blues_r", )
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax3.set_title('豆瓣影片Top250制片国家/地区统计    by:『知秋小梦』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax3.set_xlabel('影片制片国家/地区', fontsize=10)
    # 设置 x 轴标签文字的方向
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=-90)
    ax3.set_ylabel('国家/地区出现次数', fontsize=10)
    # 设置坐标轴刻度的字体大小
    ax3.tick_params(axis='x', labelsize=8)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_country_x)), movie_country_y):
        ax3.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()

    '''2.2 定距/定比特征分析'''
    # 影片片长、影片总评分、影片评论数
    ''''2.2.1 将影片片长数据通过箱型图展示'''
    ax4 = sns.swarmplot(x=np.ones(df_data.shape[0]), y='movie_run_time', data=df_data)
    ax4.set_title('豆瓣影片Top250片长分布    by:『知秋小梦』')
    ax4.set_xlabel('影片片长分布', fontsize=10)
    ax4.set_ylabel('片长（分钟）', fontsize=10)
    plt.show()

    ''''2.2.2 将影片总评分数据通过箱型图展示'''
    ax5 = sns.swarmplot(x=np.ones(df_data.shape[0]), y='movie_rating', data=df_data)
    ax5.set_title('豆瓣影片Top250总评分分布    by:『知秋小梦』')
    ax5.set_xlabel('影片总评分分布', fontsize=10)
    ax5.set_ylabel('影片总评分', fontsize=10)
    plt.show()

    ''''2.2.3 将影片评论数数据通过箱型图展示'''
    ax6 = sns.swarmplot(x=np.ones(df_data.shape[0]), y='movie_comments_user', data=df_data)
    ax6.set_title('豆瓣影片Top250评论数分布    by:『知秋小梦』')
    ax6.set_xlabel('影片评论数分布', fontsize=10)
    ax6.set_ylabel('影片评论数（个）', fontsize=10)
    plt.show()

    ''''2.2.4 将影片上映日期数据通过展示'''
    df_data_release_date_x = df_data['movie_release_date'].value_counts().index.tolist()
    df_data_release_date_y = df_data['movie_release_date'].value_counts().values.tolist()
    ax7 = sns.barplot(x=df_data_release_date_x, y=df_data_release_date_y, palette="Blues", )
    ax7.set_title('豆瓣影片Top250上映日期分布    by:『知秋小梦』')
    ax7.set_xlabel('影片上映日期', fontsize=10)
    ax7.set_ylabel('上映影片（个）', fontsize=10)
    # 设置 x 轴标签文字的方向
    ax7.set_xticklabels(ax7.get_xticklabels(), rotation=-90)
    plt.show()

    ''''2.2.5 将影片各星级评论数数据通过箱型图展示'''
    # 各星级评论数
    df_data_star = pd.DataFrame(columns=['five_star', 'four_star', 'three_star', 'two_star', 'one_star'])
    df_data_star['five_star'] = df_data['movie_comments_user']*df_data['movie_five_star_ratio']
    df_data_star['four_star'] = df_data['movie_comments_user']*df_data['movie_four_star_ratio']
    df_data_star['three_star'] = df_data['movie_comments_user']*df_data['movie_three_star_ratio']
    df_data_star['two_star'] = df_data['movie_comments_user']*df_data['movie_two_star_ratio']
    df_data_star['one_star'] = df_data['movie_comments_user']*df_data['movie_one_star_ratio']

    # 绘制组合图形
    fig, ax = plt.subplots(2, 3, figsize=(12,5))
    sns.stripplot(data=df_data['movie_comments_user'], ax=ax[0, 0])
    sns.stripplot(data=df_data_star['five_star'], ax=ax[0, 1])
    sns.stripplot(data=df_data_star['four_star'], ax=ax[0, 2])
    sns.stripplot(data=df_data_star['three_star'], ax=ax[1, 0])
    sns.stripplot(data=df_data_star['two_star'], ax=ax[1, 1])
    sns.stripplot(data=df_data_star['one_star'], ax=ax[1, 2])

    ax[0, 0].set_title('影片总评论数分布')
    ax[0, 1].set_title('影片五星评论数分布')
    ax[0, 2].set_title('影片四星评论数分布')
    ax[1, 0].set_title('影片三星评论数分布')
    ax[1, 1].set_title('影片二星评论数分布')
    ax[1, 2].set_title('影片一星评论数分布')

    plt.show()

    '''3. 组合特征分析'''
    '''3.1 影片时间+影片类型'''
    # 略

    # 中国的影片TOP之路：中国制片的影片数据
    df_data_China_x = df_data[df_data['movie_country'].str.contains('中国')]
    df_data_release_date_x_China = df_data_China_x['movie_release_date'].value_counts().index.tolist()
    df_data_release_date_y_China = df_data_China_x['movie_release_date'].value_counts().values.tolist()
    ax7 = sns.barplot(x=df_data_release_date_x_China, y=df_data_release_date_y_China, palette="Blues_r", )
    ax7.set_title('豆瓣影片Top250中国制片分布    by:『知秋小梦』')
    ax7.set_xlabel('影片上映日期', fontsize=10)
    ax7.set_ylabel('上映影片（个）', fontsize=10)
    # 设置 x 轴标签文字的方向
    ax7.set_xticklabels(ax7.get_xticklabels(), rotation=-90)
    plt.show()

    '''4. 特征查找'''
    '''4.1 影片评论数最多、最少的'''
    '''4.2 影片评分最高、最低的'''
    '''4.3 影片五星评论数最多的、最少的'''
    '''4.2 影片一星评论数最多的、最少的'''
    '''4.2 上映年份最多的那一年哪个国家上映影片最多？哪个国家制作的做多？哪种影片类型最多'''
    '''4.2 中国从什么时候起影片在突增，分析原因（柱状图）'''
    '''4.2 影片评分最高的'''

    # 中国大陆参与制作的影片
    print(df_data[df_data['movie_country'].str.contains('中国大陆')][
              ['movie_rank', 'movie_name', 'movie_release_date',
               'movie_type', 'movie_country', 'movie_language']]
          )
    # 影片时长在五十分钟以下的影片：
    print(df_data.sort_values(by='movie_run_time')[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_run_time',
               'movie_rating','movie_comments_user']].head(1))
    # # 评论数最多的前五部影片
    print(df_data.sort_values(by='movie_comments_user', ascending=False)[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))
    # 评论数最少的前五部影片
    print(df_data.sort_values(by='movie_comments_user')[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))
    print('*'*50)
    # 评分最高的前五部影片
    print(df_data.sort_values(by='movie_rating', ascending=False)[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))
    # 评分最低的前五条影片
    print(df_data.sort_values(by='movie_rating')[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))
    # 五星评分人数最多的前五部影片
    print(df_data.sort_values(by='five_star_movie_comments_user', ascending=False)[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))

    # 评分+评论数最高的前五部影片
    print(df_data.sort_values(by=['movie_comments_user', 'movie_rating'], ascending=False)[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))

    # 评论数+评分最高的前五部影片
    print(df_data.sort_values(by=['movie_comments_user', 'movie_rating'],  ascending=False)[
              ['movie_rank', 'movie_name', 'movie_release_date', 'movie_rating', 'movie_comments_user']].head(5))

    # '''思考：影片排序依据'''
    # # 影片评论数进行特征缩放：采用归一化进行特征缩放
    # min_user_x = np.min(df_data['movie_comments_user'], 0)  # 按列获取最小值
    # max__user_x = np.max(df_data['movie_comments_user'], 0)  # 按列获取最大值
    # # 归一化特征缩放
    # df_data['movie_comments_user'] = (df_data['movie_comments_user'] - min_user_x) / (max__user_x - min_user_x)
    #
    # # 影片评分进行特征缩放：采用归一化进行特征缩放
    # min_rating_x = np.min(df_data['movie_rating'], 0)  # 按列获取最小值
    # max__rating_x = np.max(df_data['movie_rating'], 0)  # 按列获取最大值
    # # 归一化特征缩放
    # df_data['movie_rating'] = (df_data['movie_rating'] - min_rating_x) / (max__rating_x - min_rating_x)
    # print(df_data['movie_rating'])

    # 通过sklearn 进行数据归一化
    from sklearn import preprocessing

    df_data['movie_rating'] = preprocessing.normalize(df_data[['movie_rating']], axis=0)
    df_data['movie_comments_user'] = preprocessing.normalize(df_data[['movie_comments_user']], axis=0)
    # 线性相关吗？画图吧
    sns.lmplot('movie_comments_user', 'movie_rating', df_data, order=4)
    ax = plt.gca()
    ax.set_title('总评分与评论数线性相关？    by:『知秋小梦』')
    ax.set_xlabel('影片评论数', fontsize=10)
    ax.set_ylabel('影片总评分', fontsize=10)
    plt.show()


if __name__ == '__main__':
    data = read_data()
    data = reshape_data(data)
    print("*"*50)
    view_data(data)
