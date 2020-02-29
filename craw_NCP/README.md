### 本项目实现如下功能：
- 爬取官方发布的新型冠状病毒的每日更新数据
- 数据处理
- 画图展示相关数据
- 邮件发送给相应列表

**备注 ：NCP（ Novel coronavirus pneumonia 新型冠状病毒肺炎）**
<br><br>
**项目详细讲解原文链接**： [写了个自动化脚本，每日更新疫情数据](https://mp.weixin.qq.com/s?__biz=MzI5MjYwNTU5NQ==&mid=2247484161&idx=1&sn=c380e1bacf77a31bc01d0f6e69306635&chksm=ec7f98f5db0811e3c04e7d6044578ea4f7714db76cfc268d03f5d169c8777a4b42519ebc58b4&token=1458385266&lang=zh_CN#rd)

<br>
<br>

### 项目讲解


#### 写在前面的话

先说明一下，这是一篇爬虫+分析+自动化的文章，并不是上节说到的 NumPy 系列文章，NumPy 系列请期待下节内容。

这篇实战文章也属于心血来潮吧，简单说一下：

小一我自从疫情发生了之后，每天早上第一件事就是关注微博热搜里面关于各地确诊人数的新闻，不得不说，确实很牵动人心，前几天的突增1w+，有点害怕，还好这几天降下来了。

最近几天和往常一样去看热搜的时候，却发现好像确诊人数的新闻并不在热搜里面，有时候还需要折腾一会才能搜到相关数据。

好吧，既然这样，那咱们就自己写一个程序，自己更新数据。

大概这篇文章的起源就是这样，就一个心血来潮的冲动，就有了。<br><br>ok，该介绍的背景都说完了，再来说下这篇文章：

`技术方面：会用到 爬虫+数据库+数据处理+绘图+邮件 相关技术`

咋一看，发现技术点还挺多，如果你经常读公众号的文章，会发现大部分知识点都有专门写过。

我都一一列出来，文章哪一块看不明白了回来查一下再继续

爬虫：动态获取数据、BeautifulSoup详解

数据库：数据库存储

邮件：邮件发送<br>
<br>

#### 正文

我们要做一个自动化的程序，当然就不只是爬虫那么简单了。

先明确一下需求：

- 爬虫获取最新疫情数据
- 数据简单清洗，保存数据库
- 绘制热力地图，与前一日数据进行比较
- 将结果以邮件形式发送
- 每日定时执行程序

大概就上面五个步骤，也不是很难嘛。画热力地图是个新知识，可能需要花一些时间

准备好了，我们就开始吧！<br><br>

##### 爬取数据

首先我们需要确定数据源，这个简单。

> 说个题外话，这次疫情期间，我感觉官方媒体还是很给力的，数据都能在第一时间公开公布，让大众知道，即使很让人担忧，**棒表情包**

其中包括卫健委、人民日报、丁香园、百度地图等，都有最新数据。

就不一一列举了，网上都能搜得到。

原文链接里面我放的是丁香园，本次爬虫我也用的是丁香园的数据。

> 再说个题外话，别整那些恶意爬虫去搞这些网站，特别是最近一段时间。慎之慎之

看一下丁香园的疫情官网，可以看到有这样一些（国内）数据

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/craw_0.png)

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/craw_1.png)

一个是地区累积确诊人数的热力分布图，一个是当前的最新数据，当然还有很多折线图，我没有截

我们需要的是每日的各个省、地市的相关数据。

检查源代码，可以看到：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/craw_2.png)

其中有三个 div 需要注意：

- class=’fold___xVOZX‘ 的 div：每个省的所有数据（总）
- class=’areaBlock1___3V3UU‘ 的 div：每个省的汇总数据（分）
- class=’areaBlock2___27vn7‘ 的 div：每个省下的所有地市数据（分）

我们需要的数据就在这三个 div 里面，再看看 div 里面有什么：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/craw_3.png)

红色的是省份汇总数据，黄色的是地市的数据，黑色的是具体数据标签。

省份汇总数据的 div 和地市的数据的 div 下面都有5个 p 标签存放数据，基本一致

5个 p 标签分别是：

- class=’subBlock1___j0DGa‘ 的 p 标签：表示省份/城市名称
- class=’subBlock2___E7-fW‘ 的 p 标签：表示现存确诊人数
- class=’subBlock4___ANk6l‘ 的 p 标签：表示累计确诊人数
- class=’subBlock3___3mcDz‘ 的 p 标签：表示死亡人数
- class=’subBlock5___2EkOU‘ 的 p 标签：表示治愈人数

数据就这些了，选择一种爬虫方式爬下来吧

> 打开页面，我第一感觉就是动态数据，不信你也可以试试

选用 selenium 进行数据爬取，我尽量贴一下核心代码，文末也有源码获取方式

```python
# 初始化 selenium
executable_path = "你本机的chromedriver.exe路径"
# 设置不弹窗显示
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=chrome_options,executable_path=executable_path)
```

你也可以选择 selenium 的弹窗显示，源码里面也有写。

```python
browser.get(url)
# 输出网页源码
content = browser.page_source
soup = BeautifulSoup(content, 'html.parser')
# 获取中国城市疫情人数
soup_city_class = soup.find('div', class_='areaBox___3jZkr').find_all('div',class_='areaBlock2___27vn7')
# 获取每一个地市的数据
# 循环省略
resolve_info(per_city, 'city')

# 获取中国省份疫情人数
soup_province_class = soup.find('div', class_='areaBox___3jZkr').find_all('div',class_='areaBlock1___3V3UU')
# 获取每一个省的数据
# 循环省略
resolve_info(per_province, 'province')	
```

循环拿到每一个省份和每一个城市的代码我没写，你知道这里面的 per_city 和 per_province 代表每一个城市和省份就行了。

解析函数里面，直接获取我们需要的几个数据

```python
# 解析省份和地市详细数据
if tag == 'city':
	# 城市
	data_name = data.find('p', class_='subBlock1___j0DGa').find('span').string
else:
	# 省份
	data_name = [string for string in data.find('p', class_='subBlock1___j0DGa').strings][0]
# 现存确诊人数
data_curr_diagnose = data.find('p', class_='subBlock2___E7-fW').string
# 累计确诊人数
data_sum_diagnose = data.find('p', class_='subBlock4___ANk6l').string
# 死亡人数
data_death = data.find('p', class_='subBlock3___3mcDz').string
# 治愈人数
data_cure = data.find('p', class_='subBlock5___2EkOU').string
```

当然会存在一些特殊情况

比如：有的省份最下面有特殊注释，有的数据是空缺的等等，合理处理就行了

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/craw_4.png)

好了，数据已经全部拿到了，爬虫就算结束了。

##### 数据清洗

拿到数据以后，大致看了一眼，还算比较规整的。

在数据中，我发现了两处需要处理的地方

- 数据存在空值
- 部分地市名称其实并不是地市名称

就拿北京来说，看一下数据：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/preprocess_0.png)

黄颜色标出的是缺失数据，红颜色的是非正常名称

我是这样处理的：

第一处地方：`官网的数据并没有0，所有这个空值就是0，直接填充就可`

第二处地方：`部分数据名称不对，根据需求剔除或者合并到省会城市都可`

看一下源代码：

```python
# 删除地市的不明确数据
if tag == 'city':
    df_data.drop(index=df_data[df_data['city'] == '待明确地区'].index, axis=1,inplace=True)
    # df_data.drop(df_data['city'] == '外地来京人员', axis=1, inplace=True)
    # df_data.drop(df_data['city'] == '外地来沪人员', axis=1, inplace=True)
    # df_data.drop(df_data['city'] == '外地来津人员', axis=1, inplace=True)

# 填充空记录为0
df_data.fillna(0, inplace=True)
# 增加日期字段
df_data['date'] = time_str
```

代码应该都能看懂，就不解释了，日期字段是为了方便取出近两天的数据进行比较

接下来就是导数据到数据库了，一共两种表，省份数据表和地市数据表。

看一下数据库表结构：

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/preprocess_1.png)

`省份表类似，只是把城市名换成了省份名。`

当然，你要觉得两张表麻烦，一张表也可以存这些数据，看你自己。

`对于我们的 DataFrame 类型的数据，是可以直接导入数据库的`

一行代码就行，看好了

```python
# 连接数据库
connect = create_engine('mysql+pymysql://username:passwd@localhost:3306/db_name?charset=utf8')
# 保存数据到数据库中
df_data.to_sql(name=table_name, con=connect, index=False, if_exists='append')
```

> 你不会觉得连接数据库也算一行吧？那就两行，给大哥跪下

数据搞定了，下面开始绘图

##### 数据绘图

我们要画的是热力地图，直接用 pyecharts，上手简单

> 用 echarts 的原因是我曾经写过一段时间前端代码，echarts研究过一段时间，比较容易上手

这里需要安装两个模块 pyecharts 和 ，用来画图和输出成图片保存

`安装也很简单， cmd 下直接输入 pip install 模块名称`

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/0_install_pyecharts.png)

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/1_install_snap.png)

模块包安装没有问题的话就可以画图了

```python
# 导入相应模块
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot

"""绘制热力地图"""
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
```

看着效果还不错。

需要提到的是，我们需要的是`省份/地市名称+累积确诊人数`两列数据

它们对应的是第二列和第四列，所以上面代码是这样写的

```python
df_data.iloc[:, [1, 3]]
```

还有一些地图的控件设置，看懂是什么意思就行了，不会了再去查API文档

> 我有挨个行写注释，你可别说你看不懂

图片生成了，看看张什么样子

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/plot_0.png)

根据每日的数据更新，我们比较最近两天的增长情况，做一个表格出来

获取到最近两天的数据库数据

```python
# 设置日期
data_time = datetime.now() + timedelta(-2)
data_time_str = data_time.strftime('%Y-%m-%d')
# 获取数据库近两天的数据
sql_province = 'select * from t_ncp_province_info where date>={0}'.format(data_time_str)
df_province_data = pd.read_sql_query(sql_province, connect)
```

将数据按天分成两部分，做差即可，直接贴代码

```python
# 获取数据日期
date_list = df_data['date'].drop_duplicates().values.tolist()
# 根据日期拆分dataframe
df_data_1 = df_data[df_data['date'] == date_list[0]]
df_data_2 = df_data[df_data['date'] == date_list[1]]
# 昨天-前天 比较新增数据
df_data_result = df_data_2[['curr_diagnose', 'sum_diagnose', 'death', 'cure']] - df_data_1[['curr_diagnose', 'sum_diagnose', 'death', 'cure']]
```

更进一步的，计算数据的环比增长率

```python
# 新增较上一日环比列
df_data_result['curr_diagnose_ratio'] = (df_data_result['curr_diagnose']/df_data_1['curr_diagnose']).apply(lambda x: format(x, '.2%'))
df_data_result['sum_diagnose_ratio'] = (df_data_result['sum_diagnose']/df_data_1['sum_diagnose']).apply(lambda x: format(x, '.2%'))
df_data_result['death_ratio'] = (df_data_result['death']/df_data_1['death']).apply(lambda x: format(x, '.2%'))
df_data_result['cure_ratio'] = (df_data_result['cure']/df_data_1['cure']).apply(lambda x: format(x, '.2%'))
```

如果要在邮件中显示表格内容，我们还需要对列名进行排序和更改

并且根据相应的数据进行降序排序，这样增长变化看起来更明显

```python
if tag == 'city':
	name = '城市'
else:
	name = '省份'

df_data = df_data[[tag, 'sum_diagnose', 'sum_diagnose_ratio', 'curr_diagnose',
'curr_diagnose_ratio', 'death', 'death_ratio', 'cure', 'cure_ratio']]
df_data.rename(
	columns={
    	tag: name,
		'sum_diagnose': '累计确诊人数',
		'sum_diagnose_ratio': '累计确诊环比增长率',
        'curr_diagnose': '现存确诊人数',
        'curr_diagnose_ratio': '现存确诊环比增长率',
        'death': '死亡人数',
        'death_ratio': '死亡环比增长率',
        'cure': '治愈人数',
        'cure_ratio': '治愈环比增长率'
    }, inplace=True
)

# 数据排序
df_data.sort_values(['累计确诊人数', '累计确诊环比增长率'], inplace=True, ascending=False)
df_data.reset_index(inplace=True)
```

ok，以上的数据，包括生成的图片都是我们需要在邮件中显示的。

##### 邮件发送

邮件中，需要加入上一步的图片和表格数据，添加到正文中发送

因此，邮件正文需要设置成 html 格式发送。

并且我们在正文中需要插入近两天的数据，所以 html 中需要这样设置

```python
# 部分 html 内容
'<p><img src="cid:image1" alt="最新数据地图" width="1200" height="600"></a></p>'
'<p><img src="cid:image2" alt="最新数据地图" width="1200" height="600"></a></p>'
```

根据 cid 区分不同的照片，同样的，需要在邮件中这样设置

```python
# 读取图片并创建MIMEImage
for i, imag_filepath in enumerate(img_path_list):
	with open(imag_filepath, 'rb') as fp:
    	msg_image = fp.read()
    msg_image = MIMEImage(msg_image)
    # 定义图片 ID，在 HTML 文本中引用
    msg_image.add_header('Content-ID', '<image{0}>'.format(i + 1))
    message.attach(msg_image)
```

另外，邮件中设置 html 格式正文也需要设置

```python
# 设置主题
subject = '截止 ' + date_str + ' 疫情最新数据（自动推送）'
# 设置发送内容:1：发送html表格数据
message = MIMEMultipart()
# 生成邮件正文内容
emain_content = get_email_content(df_data_1, df_data_2)
send_text = MIMEText(emain_content, 'html', 'utf-8')
message.attach(send_text)
```

具体的邮件发送教程可以看最前面提到的，之前写的很详细

如果没有什么异常，你会收到这样的一封邮件

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/email_0.png)

![文章首发：公众号『知秋小梦』](https://raw.githubusercontent.com/double-point/GraphBed/master/craw_ncp/email_1.png)

##### 定时任务

程序基本上已经算是完成了，自动化这一步提供一个方法，大家参考即可：

- Linux下：`可以使用 crontab 设置定时任务`
- Win下：`可以使用（控制面板搜）任务计划程序设置定时任务`

另外，我已经部署好了自己的定时任务，`如果有需要的同学可以在公众号评论区留言自己的邮箱` ，每天早上定时更新<br><br>

#### 总结一下：

先列好需求，再把需求一个个实现了，其实今天的项目就比较清晰明了了。

一个五个需求，我们再回顾一下：

- 爬虫获取最新疫情数据
- 数据简单清洗，保存数据库
- 绘制热力地图，与前一日数据进行比较
- 将结果以邮件形式发送
- 每日定时执行程序

最后一步大家可以先百度，以后我会专门拎出来写一节，可以自动化的任务它不香吗？<br><br>


有需要交流学习的同学可以加我们的交流群。（公众号后台回复`加群`）<br><br>

#### 写在后面的话

疫情还没过去，下周大家伙应该都要上班了

我已经窝了两星期，虽然特别想出来，但是一想到上下班的人，我就有点怂。

不多说了，下周上班，我们都要保护好自己。

##### 碎碎念一下

> 对了，需要每天定时邮件更新疫情数据的同学请在公众号评论区留自己的邮箱
>
> 我们评论区见

<br>

##### 原创不易，欢迎点赞噢

> 文章首发：公众号【知秋小梦】 
>
> 文章同步：掘金，简书

<br>

<br>
