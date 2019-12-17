##### 爬取豆瓣电影信息
```
# encoding:utf-8
# FileName: craw_douban_movie
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/6 15:50
# Description: 爬取豆瓣电影数据
```
#### 数据类型
```
movie_rank：影片排序
movie_name：影片名称
movie_director：影片导演
movie_writer：影片编剧
movie_starring：影片主演
movie_type：影片类型
movie_country：影片制片国家
movie_language：影片语言
movie_release_date：影片上映日期
movie_run_time：影片片长
movie_second_name：影片又名
movie_imdb_href：影片IMDb 链接
movie_rating：影片总评分
movie_comments_user：影片评论人数
movie_five_star_ratio：影片5星占比
movie_four_star_ratio：影片4星占比
movie_three_star_ratio：影片3星占比
movie_two_star_ratio：影片2星占比
movie_one_star_ratio：影片1星占比
movie_note：影片备注信息，一般为空
```


#### 逻辑类型
> 起始页码：start_page
> 每一页大小：page_size
> 总页码： pages


#### 注意事项
> 每个数据的数据类型都应该为字符类型，在爬虫中不做处理（在数据清洗中做数据处理）
> 爬虫中注意 beautifulsoup 的使用
> 总排名中显示每个影片的信息，进入详情页面可以看到详情信息，包括评论和每个星级的打分情况
> 影评信息在 JSON 中获取，其他信息均在页面中可直接拿到
> 个别影片不存在 "又名"，需要注意
> 个别影片中制片国家/地区包括多个国家地区，需要注意数据库中数据类型长度