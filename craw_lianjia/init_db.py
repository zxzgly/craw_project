# encoding:utf-8
# FileName: init_db
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/25 16:12
# Description: 创建数据库表对象并建立和数据库的连接

#  创建基类
from sqlalchemy import create_engine, Column, INTEGER, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DoubanMovieTop250(Base):
    """
    创建表
    """
    __tablename__ = 't_lianjia_rent_info'

    # 表的结构:
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    house_id = Column(String(50))
    house_address = Column(String(200))
    house_longitude = Column(String(50))
    house_latitude = Column(String(50))

    house_rental_method = Column(String(50))
    house_layout = Column(String(20))
    house_rental_area = Column(String(20))
    house_orientation = Column(String(20))
    house_rental_price = Column(String(20))
    house_update_time = Column(String(50))
    house_floor = Column(String(20))

    house_tag = Column(String(200))
    house_elevator = Column(String(20))
    house_parking = Column(String(20))
    house_water = Column(String(20))
    house_electricity = Column(String(20))
    house_gas = Column(String(20))
    house_heating = Column(String(20))
    house_note = Column(String(200))
    create_time = Column(Date)


def connection_to_mysql():
    """
    连接数据库
    @return:
    """
    engine = create_engine('mysql+pymysql://username:password@localhost:3306/db_data_analysis?charset=utf8')
    Session = sessionmaker(bind=engine)
    db_session = Session()
    # 创建数据表
    Base.metadata.create_all(engine)

    return engine, db_session


if __name__ == '__main__':
    pass