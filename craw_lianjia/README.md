#### 爬取链家房产信息

定位：链家网->租房<br>
并进行相应的数据分析

代码详细讲解请点击：[爬虫实战—拿下最全租房数据 | 附源码](http://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247484012&idx=1&sn=50aa0f8034d51981346ee36fb34da6a1&chksm=ec7f9998db08108edf9e08ac3dd680093bafb42684303dea28e4551a9a6e74a37cb9fbfe14d9&token=1239705701&lang=zh_CN#rd)
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
> 若通过区域之后，有区域数据仍超过3300条，可以通过设置房屋出租方式、房屋面积进行二次限定<br><br>
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

<br><br>
#### 爬虫流程


<br>

#### 爬取某家网租房信息

<br><br>

> 点赞再看，养成好习惯<br><br>Python版本3.8.0，开发工具：Pycharm

<br><br>

#### 写在前面的话

老规矩，目前为止，你应该已经了解爬虫的三个基本小节：

- [爬虫的原理和流程](https://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247483880&idx=1&sn=7b3c4461cd3d2e9e26db8eb3918bff74&chksm=ec7f9a1cdb08130af14247f4be2ead36590fc96233f24028333ca8da74c5e40990979f70f43e&token=109866799&lang=zh_CN#rd)
- [爬虫的两种实现方式](https://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247483938&idx=1&sn=d132924fdb72f15189af959237086f33&chksm=ec7f99d6db0810c057bf2e8dc6560cf53f86406b6a632c4584e9867bfd96cdd78cec05f3fde4&token=590259903&lang=zh_CN#rd)
- [通过 BeautifulSoup 解析网页源码](https://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247483891&idx=1&sn=a5fabdd931073088bf95d89ed0de7cb2&chksm=ec7f9a07db08131196a351d63e3170aea9889ca761ae22ed53e86dab21244eb7ef32383acec3&token=109866799&lang=zh_CN#rd)

不了解的自行`点进去复习`。

上一篇的实战只是给大家作为一个练手，数据内容比较少，且官网也有对应的 API，难度不大。

但是“麻雀虽小，五脏俱全”，如果这一节看完感觉流程还不是很熟悉，建议去看上一节：

- [爬虫实战-手把手教你爬豆瓣电影](https://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247483908&idx=1&sn=674e024fc361f30013fe742175fc8bc0&chksm=ec7f99f0db0810e629c765de69575fe757a522a72ab75a790bfb506bdab65a2b3c71c3a11a7c&token=590259903&lang=zh_CN#rd)<br>

好了，前面的回顾就到此为止。这节开始带大家`真正搞事情`。

<br>

#### 准备工作

**确定目标**

今天我们的目标是某家网，官网链接：https://www.lianjia.com/。

当你用浏览器访问这个网址的时候，可能会自动变成 https://sz.lianjia.com/ 这种。

`sz` 代表的是城市`深圳`。<br>（哈哈，是的，小一我现在在深圳。）<br><br>某家网上有二手房、新房、租房等等，我们今天的目标是 https://sz.lianjia.com/zufang/ <br>“你没看错，`zufang` 是 `租房` 的拼音“<br><br>所以，今天我们要爬取某家网的租房数据，地点：深圳。<br><br>**设定流程**

> 因为官网的数据每天都在发生变化，你也不必说要和我截图中的数据一模一样。

首先，我们已经确定了目标是`某家网在深圳的所有租房数据`，看一下首页

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/1.png)

截止2019-12-31号，深圳十个区共 32708 套深圳租房，好像还挺多的，不知道我们能不能全部爬下来。

按照官网`每页30条数据`来看，我们看一下翻页的显示：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/2.png)

问题来了，显示页码只有100页，是不是100页之后被隐藏了呢？

我们试着在 url 中修改页码为pg101，结果发现显示的还是第100页的内容。<br><br>**那，如何解决网页只有前100页数据？**

`设置搜索条件`，确保每个搜索条件下的数据不超过3000条，这样我们就可以通过100页拿到所有的数据。<br><br>通过`设置区域`进行搜索，试试看：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/3.png)

罗湖区 2792条数据 < 3000。

ok，我们再看看其他区

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/4.png)

好像不太妙，福田区`整租`都有4002套（已经设置了`整租`条件的情况下）。

没关系，我们继续设置搜索条件：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/5.png)

新增居室搜索，可以看到福田区整租的一居有1621套，满足条件。

其他三个直接不用看了，肯定也满足。

继续查看剩余的几个区，发现也满足，搞定<br><br>

那这样子的话，我们的步骤就是先检查记录数有没有超过3000条，超过了则继续增加新的条件，一直到不超过3000，然后分页遍历所有数据。

好，那我们稍微画一下流程图：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

**确定条件**

大致流程基本没什么问题了，我们看一下具体需要注意的搜索条件。

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/9.png)<br>首先是`城市区域`的获取，每个城市的区域都不一样，区域数据通过网页获取

其次是`出租方式`的获取，官网对应两种：`整租和合租`，观察 url 发现分别对应 `rt200600000001、rt200600000002`

然后是房屋居室的获取，官网对应四种：`一居、二居、三居和四居`，观察 url 发现分别对应 `l0、l1、l2、l3`（小写字母 L 不是1）

最后是分页的获取，官网 url 对应 `pg+number`。

拼接成 url 之后是：<br>`base_url+/区域/+pg+出租方式+居室`<br><br>**细节处理**

- 爬取的内容较多，每次爬取需要设置时间间隔
- 需要增加浏览器标识，防止被封 ip
- 需要增加检测机制，丢掉已经爬取过的数据
- 数据需动态保存在文件中，防止被封后需要重头再来
- 若要保存数据库，爬虫结束后再连接数据库

<br>**异常处理**

官网中有一种类型的房屋，网页格式不标准，且拿不到具体数据。

对，就是`公寓`。

可以看到，在房屋列表中公寓无论是在价格显示、房屋地址、朝向等都异于普通房屋。

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/16-1.png)<br>

且在详细界面的内容也是无法拿到标准信息的

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/lianjia_rent_craw/16-3.png)

对于这种数据，我们直接丢掉就好。

<br>

**原创不易，欢迎点赞噢**
> 文章首发：公众号【知秋小梦】 <br><br>文章同步：掘金，简书，csdn

<br>

<br><br>