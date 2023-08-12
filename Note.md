# 记录一次对积目APP的逆向过程

> 这次的一个小收获是可以查看部分积目用户的具体位置以及坐标。

我们的思路很简单，使用逆向三板斧（抓包、静态分析、动态分析）

## 抓包

正常抓包无法查看HTTPS协议的包，在这里我们使用XP模块对SSL Pinning进行解除。

XP模块注入后，我们已经可以看到HTTPS协议的数据包了，我们对主要的几个API Endpoint进行审计。

![image](https://github.com/Evil0ctal/JiMu-APP-Client/assets/20760448/afd94a50-bfe7-412c-8e6f-fe2fcef8f5fb)


可以看到在`我的->访客`这个view中被发出的请求在响应时没有对数据做过滤，返回了`lat` 和 `lng`这两个坐标数据，在下面的演示JSON中去除了个人信息。

```json
{
               "visit_time":1691634089,
               "un_read":0,
               "user_info":{
                  "id":"xxxxxxxx",
                  "user_tag":"超爱聊天",
                  "is_expand_covers":0,
                  "address":"",
                  "age":21,
                  "authStatus":-1,
                  "face_status":0,
                  "city":"",
                  "constellation":"白羊座",
                  "createTime":"2020-08-15 04:58:50",
                  "distance":12.887182889398028,
                  "gender":2,
                  "lat":37.30890306084834,
                  "lng":-121.9135438673637,
                  "nickname":"很不听话"
               }
            }
```

根据经验判断，`lat` 和 `lng`看起来是标准的[WGS 84](https://en.wikipedia.org/wiki/World_Geodetic_System)坐标系统格式，这是Google Maps所使用的坐标格式。我们可以直接在Google Maps中使用这些坐标。

使用Google Maps构建位置URL：

`https://www.google.com/maps/?q=纬度,经度`

构建完成的URL：

`https://www.google.com/maps/?q=48.18108406871809,-114.3050911575964`

点击链接我们就能直接查看用户上一次打开积目APP时的位置了。

至此我们的目的已经达到，但是为了更加快速的获取用户位置，我们需要写一个脚本直接与积目APP的API进行通讯，于是我们继续观察刚刚抓到的数据包。

请求头：
```
Authorization: InkeV1 amltdTpHTQ:qa7ZGK8WDZJ/8gTJh8kuxCZ3vaw=
Client-TimeStamp: 1691800006456
Host: service.hitup.cn
Connection: Keep-Alive
Accept-Encoding: gzip
User-Agent: okhttp/4.1.1
```

我们可以看到，在请求头中有一个`Authorization: InkeV1 amltdTpHTQ:uc68b/fprWDmrt36Ob+5mZ4H2uQ=`字段，看起来是一个加密，应该是用于给后端校验请求合法性的，于是我们尝试去掉该字段进行发包请求，果然服务器不再响应数据。

现在我们知道了加密的具体参数名，我们回到电脑进行下一步分析。

## 静态分析
