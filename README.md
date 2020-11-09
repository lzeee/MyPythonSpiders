# 个人简单爬虫项目

⭐表示难度评价
- [落霞小说⭐](#落霞小说)  
- [冥想材料⭐](#冥想材料)  
- [百度街景爬虫⭐⭐](#百度街景爬虫)
- [高德通行时长爬虫⭐⭐](#高德通行时长爬虫)
- [日本Foursquare爬虫⭐⭐](#日本Foursquare爬虫)
- [爱奇艺弹幕爬虫⭐⭐](#爱奇艺弹幕爬虫)
- [北大未名BBS爬虫⭐⭐](#北大未名BBS爬虫)  
- [Youtube爬虫⭐⭐⭐](#Youtube爬虫)  
- [天眼查企业信息爬虫⭐⭐⭐](#天眼查企业信息爬虫)

## 落霞小说
最简单的练手项目，爬取 [落霞小说网](https://www.luoxia.org/) 上的一本小说《知否》。这个网站连搜索功能都没有，也不知道能活多久。爬取小说需要先随便选本书，确定对应的url，F12打开开发者模式人工分析html的规则即可。

爬取过程分两步
* 收集每个章节的url
* 下载每个章节的内容

其中需要注意的点，一是该网站为了反爬，同样的标签内容可能有不同的形式，可以人工确定所有形式，用正则提取url；二是加入了一些公众号推广相关的段落，和小说内容无关，需要去掉；三是请求频率过高会被封ip，最简单的用sleep来降低请求频率防止被封。

## 冥想材料
之前有一段时间超级崇拜冥想（冥想和宗教无关，我理解它就是一种放松的方式，很多国家从小学开始就推广冥想课程），无奈冥想课程都很贵，尤其国内基本没有比较优质的免费资源。所以从[ mindful](https://www.mindful.org/) 上爬取了一套免费教程。唯一的缺点就是内容全英文，好难听懂啊QAQ

相比第一个爬虫，此爬虫就涉及到一点更复杂的知识Cookie。用户需要登录才能看到课程的内容，所以用Python模拟发送请求时，如何假装自己是真实的用户呢？这里用最简单的方式，手动打开网站并登录，F12打开开发者模式，分析登录请求，手动复制Cookie并在程序中发送请求时使用。



## 百度街景爬虫
> 用来爬取百度街景的图片数据
> 实际使用时，需要注意坐标问题，不同坐标系以及区分投影坐标/地理坐标

## 高德通行时长爬虫
> 用高德API计算两地之间，不同交通方式的时长
> 需要申请key，有配额限制，量大的话需要多个key

## 日本Foursquare爬虫
> 根据经纬度爬取POI点，根据POI点爬取评分、签到量等信息
> 待整理


## 爱奇艺弹幕爬虫
> 爬取某个电视剧的弹幕，并分析情感
> 待整理

## 北大未名BBS爬虫
爬取BBS，十大帖子以及热门版面，简单词频分析，用echarts可视化
由于版面访问限制，需要用BBS账号密码登录

## Youtube爬虫
> 暂时失效
> 通过爬取相应的爬取服务来爬取视频
> 爬取youtube上的视频和字幕，主要是为了爬取一些优秀的计算机课程
> b站：https://space.bilibili.com/12877013

## 天眼查企业信息爬虫
> 爬取某年时间某地区对应的某类企业的所有信息
> 点击验证码
> 待整理
