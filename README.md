# JiMu-APP-Client
积目APP的网页客户端，将积目的API进行封装调用。

Github: [https://github.com/Evil0ctal/JiMu-APP-Client/](https://github.com/Evil0ctal/JiMu-APP-Client/)

# 运行

> 确保80端口放行

- `git clone https://github.com/Evil0ctal/JiMu-APP-Client.git`
- `cd JiMu-APP-Client\`
- `pip3 install -r requirements.txt`
- `python3 JiMuWeb.py`

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

```python
location_url = f"https://www.google.com/maps/?q={lat},{lng}"
print(location_url)
```

构建完成的URL：

`https://www.google.com/maps/?q=37.30890306084834,-121.9135438673637`

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

我们使用Jadx对APK文件进行反编译，但是发现该APK已经被加壳了。

![image](https://github.com/Evil0ctal/JiMu-APP-Client/assets/20760448/8bf1cfe6-e680-42f4-9298-82d2cda088bf)

这种情况下，我们只能对APK进行砸壳，在这里我使用[FRIDA-DEXDump](https://github.com/hluwa/frida-dexdump)对加载到手机内存中的DEX文件进行砸壳。

砸壳完成后，我们得到了非常多的DEX文件，这是因为FRIDA-DEXDump会对内存中的所有DEX文件进行扫描，并把有关联的DEX全部输出。

现在我们使用Jadx重新打开输出的DEX文件，并直接搜索加密参数关键字，在这里我搜索的是`InkeV1`关键字，因为这看起来像一种固定的加密格式，写过后端的同学应该知道，类似JWT。

非常走运，开发者没有对这个String进行编码，我们直接在代码中搜到了该值。

![image](https://github.com/Evil0ctal/JiMu-APP-Client/assets/20760448/61947f32-e906-4f9c-9e9b-9012adeb7941)

点进该方法，查看代码逻辑。

![image](https://github.com/Evil0ctal/JiMu-APP-Client/assets/20760448/e17cb0af-8768-4909-b35d-8fbc845aecbd)

现在的思路就很明了了，请求头中包含一个时间戳，然后对HTTP的请求方法进行了判断(GET/POST)，根据请求方法+时间戳+设备信息+APK版本+HTTP查询参数进行加密。

## 动态调试

使用frida对入口函数的参数进行输出，根据调用栈继续跟踪加密所使用的参数即可，费时费力我这里就不演示了，所有的加密都在JAVA层进行计算，没有设计Native层。

## 总结

积目APP的开发者在客户端似乎没有使用到这些坐标数据，理论上应该要对这些数据进行过滤，因为观察到在其他API端点请求用户数据时，后端对这些字段已经做了屏蔽。

