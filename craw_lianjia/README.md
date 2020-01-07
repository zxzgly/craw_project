#### 爬取链家房产信息

定位：链家二手房->租房<br>
并进行相应的数据分析

```
# encoding:utf-8
# FileName: __init__.py
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/24 0:04
# Description: 爬取并分析链家租房数据
```

#### 数据类型
```
city: 城市
house_id：房源编号
house_rental_method：房租出租方式：整租/合租/不限
house_address：房屋地址：城市/行政区/小区/地址
house_longitude：经度
house_latitude：纬度
house_layout：房屋格局
house_rental_area：房屋出租面积
house_orientation：房屋朝向
house_rental_price：房屋出租价格
house_update_time：房源维护时间
house_tag：房屋标签
house_floor：房屋楼层
house_elevator：是否有电梯
house_parking：房屋车位
house_water：房屋用水
house_electricity：房屋用电
house_gas：房屋燃气
house_heating：房屋采暖
create_time：创建时间
house_note：房屋备注

# 额外字段
house_payment_method：房屋付款方式：季付/月付
housing_lease：房屋租期
```

<br><br>
#### Tips
> 链家只能爬取100页的数据，超过100页修改url也无法访问，即100*33=3300条数据<br>
> 通过区域爬取，例如深圳市租房信息3w+，一共有10个行政区，通过行政区进行第一次划分<br>
> 若通过区域之后，有区域数据仍超过3300条，可以通过设置房屋出租方式、房屋面积进行二次限定<br><br><br>
> 链家网对于整租房屋会显示其面积，对于合租房屋会隐藏面积勾选，（合租一般面积都比较小，符合正常思维）<br>
> 但实际整租、合租都可以通过房屋面积进行二次筛选
```
列出可能会用到的一些筛选指标：

深圳市行政区域共有：
罗湖区、福田区、南山区、盐田区、宝安区、龙岗区、龙华区、光明区、坪山区、大鹏新区
luohuqu、futianqu、nanshanqu、yantianqu、baoanqu、longgangqu、
longhuaqu、guangmingqu、pingshanqu、dapengxinqu
对应网站链接显示：https://sz.lianjia.com/zufang/luohuqu/

链家网对于房屋出租方式的限制分别为：
整租、合租
rt200600000001、rt200600000002
对应网站链接显示：https://sz.lianjia.com/zufang/luohuqu/rt200600000001/

链家网对于房屋布局的限制分别为：
一居、二居、三居、四居+
l0、l1、l2、l3
对应网站链接显示：https://sz.lianjia.com/zufang/luohuqu/l0/

链家网对于房屋面积的限制分别为：
<=40平米、40-60、60-80、80-100、100-120、>120
ra0、ra1、ra2、ra3、ra4、ra5
对应网站链接显示：https://sz.lianjia.com/zufang/luohuqu/rax0/

```

<br><br>
#### 逻辑设计
> 链家网租房主页面：https://sz.lianjia.com/zufang/<br><br>
> 从深圳市的每个区获取数据 
> 输入每个区的网址数据网址，例如罗湖区：https://sz.lianjia.com/zufang/luohuqu/<br><br>
> 根据页面显示的数据条数（是否超过3000），确定是否进行二次划分<br>
> 若超过3000条记录，则新增房屋出租方式筛选，进行二次划分查询。
例如：罗湖区整租：https://sz.lianjia.com/zufang/luohuqu/rt200600000001/<br>
> 若二次划分结果仍超过3000条记录，则新增房屋居室情况筛选，进行三次划分查询。
例如：罗湖区一居室 ：https://sz.lianjia.com/zufang/luohuqu/rt200600000001l0/<br><br>
> 针对每个区的租房信息，通过构建新的 url 获取每一个页面<br><br>
> 每个页面有30个房屋大致信息，获取房屋链接进入详细页面获取信息<br><br>
> 通过修改url中页码参数进行翻页，其中链接格式如下： https://sz.lianjia.com/zufang/luohuqu/pg3rt200600000001l0/<br><br>
> 所以，格式如下：<br>
> 主页面url/区域/page+出租方式+面积

<br><br>
#### 注意事项
> 注意有部分房屋属于公寓类型，房屋详细数据页面与普通房屋详细页面不同<br>
> 增加每次的休眠时间防止被封<br>
> 增加多个浏览器标识<br>
> 每爬取50条记录保存到文件中<br>
> 每爬取1000条记录需要手动确认是否继续，若不继续，则保存数据库后退出<br>
> 爬取时间较长，所以在保存数据的时候进行数据库连接。<br>