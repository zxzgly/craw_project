# encoding:utf-8
# FileName: init_db
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/14 16:18
# Description: 

# 创建对象的基类:
from sqlalchemy import create_engine, Column, String, Text, DATETIME, FLOAT, INT, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#  创建基类
Base = declarative_base()


class DoubanMovieTop250(Base):
    """
    创建表
    """
    __tablename__ = 't_douban_movie_top_250'

    # 表的结构:
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    movie_rank = Column(String(20))
    movie_name = Column(String(200))
    movie_director = Column(String(200))
    movie_writer = Column(String(200))
    movie_starring = Column(Text)
    movie_type = Column(String(100))
    movie_country = Column(String(100))
    movie_language = Column(String(100))
    movie_release_date = Column(String(100))
    movie_run_time = Column(String(100))
    movie_second_name = Column(String(200))
    movie_imdb_href = Column(String(200))
    movie_rating = Column(String(20))
    movie_comments_user = Column(String(20))
    movie_five_star_ratio = Column(String(20))
    movie_four_star_ratio = Column(String(20))
    movie_three_star_ratio = Column(String(20))
    movie_two_star_ratio = Column(String(20))
    movie_one_star_ratio = Column(String(20))
    movie_note = Column(String(200))


def connection_to_mysql():
    """
    连接数据库
    @return:
    """
    engine = create_engine('mysql+pymysql://wzg:wzg1234qq.com@localhost:3306/db_data_analysis?charset=utf8')
    Session = sessionmaker(bind=engine)
    db_session = Session()
    # 创建数据表
    Base.metadata.create_all(engine)

    return engine, db_session


if __name__ == '__main__':
    engine, db_session = connection_to_mysql()

