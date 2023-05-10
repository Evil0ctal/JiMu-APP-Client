import asyncio
import configparser

# PyWebIO support
from pywebio import *
from pywebio import config as pywebio_config
from pywebio.input import *
from pywebio.output import *
from pywebio_battery import *

# Flask support
from flask import Flask
from pywebio.platform.flask import webio_view

# JiMu support
from JiMuAPI import JiMuAPI

app = Flask(__name__)
# 初始化JiMuClient
jmc = JiMuAPI()

# 读取配置文件
webapp_config = configparser.ConfigParser()
webapp_config.read('config.ini', encoding='utf-8')
webapp_config = webapp_config['Web']

title = webapp_config['title']
version = webapp_config['version']
description = webapp_config['description']

# 演示模式
demo_mode, demo_sid, demo_uid = (True, webapp_config['demo_sid'], webapp_config['demo_uid']) \
    if webapp_config['demo_mode'] == 'True' else (False, None, None)


def demo_mode_notification():
    if demo_mode:
        put_html('<br>')
        put_markdown('已开启Demo模式，为安全考虑该功能不可用，其他功能正常使用。')
        put_link('返回首页', '/')
        return True


def register():
    clear('account')
    put_html('<br>')
    put_markdown('# 注册积目')
    put_markdown('注册功能暂时没写完，请使用积目APP注册后再使用积目Web登录。')
    put_link('返回首页', '/')


def login():
    clear('account')
    with use_scope('account'):
        # 读取Cookie判断是否已经登录
        sid = get_cookie('sid')
        uid = get_cookie('uid')
        if sid and uid:
            with use_scope('account'):
                put_html('<hr>')
                put_table([
                    ['状态', '信息'],
                    ['SID', sid],
                    ['UID', uid],
                ])
                put_markdown('你已经登录了！')
                put_buttons(['退出登录'], onclick=[logout])
                put_link('返回首页', '/')
                return
                # 未登录则显示登录界面
        data = input_group('登录积目', [
            input('国家代码', name='country_code', type=TEXT, required=True, help_text='📎输入国家代码',
                  placeholder='例如中国:86, 美国:1'),
            input('手机号', name='phone', type=TEXT, required=True, help_text='📎输入手机号', placeholder='650xxx1234'),
            input('密码', name='password', type=PASSWORD, required=True, help_text='📎输入密码',
                  placeholder='密码会自动转换为MD5保证安全'),
        ])
        try:
            r = asyncio.run(jmc.login(int(data['country_code']), int(data['phone']), data['password']))
            with use_scope('account'):
                # 登录成功后将返回JSON数据显示在页面上
                put_html('<hr>')
                put_table([
                    ['状态', '信息'],
                    ['登录状态', r['message']],
                    ['SID', jmc.sid],
                    ['UID', jmc.uid],
                ])
                put_html('<hr>')
                put_markdown('登录成功后，你可以使用积目的其他功能了！')
                put_markdown('如果你想要退出登录，可以点击下方的按钮  (·•᷄ࡇ•᷅ ）')
                put_buttons(['退出登录'], onclick=[logout])
                put_link('返回首页', '/')
                # 设置Cookie
                set_cookie('sid', jmc.sid)
                set_cookie('uid', jmc.uid)
                return jmc
        except ValueError as e:
            with use_scope('account'):
                put_html('<hr>')
                put_markdown(f'登录失败！{e}')
                put_buttons(['重新登录'], onclick=[login])
                put_link('返回首页', '/')


def clear_cookie():
    set_cookie('sid', '')
    set_cookie('uid', '')


def logout():
    clear_cookie()
    clear('account')
    with use_scope('account'):
        put_html('<hr>')
        put_markdown('你已经退出登录了！')
        put_buttons(['重新登录'], onclick=[login])
        put_link('返回首页', '/')


def put_json(data):
    with use_scope('json'):
        put_html('<hr>')
        put_markdown('完整的JSON格式数据：')
        put_code(data, language='json')
        put_html('<hr>')


def display_account_data(data: dict):
    with use_scope('account'):
        # 检查登录状态
        if data['code'] != 0:
            clear_cookie()
            put_markdown(data["message"])
            put_buttons(['重新登录'], onclick=[login])
            put_link('返回首页', '/')
            return False
        # 整理JSON
        data = data.get('data').get('accountInfo') or data.get('data')
        put_markdown('# 账户信息：')
        put_markdown(f"ID: `{data['id']}`")
        put_markdown(f"昵称: {data['nickname']}")
        put_markdown(f"省会: {data['province']}")
        put_markdown(f"城市: {data['city']}")
        put_markdown(f"距离: {data['distance']} km")
        put_markdown(f"性别: {'男' if data['gender'] == 1 else '女'}")
        put_markdown(f"签名: {data['sign']}")
        put_markdown(f"生日: {data['birthday']}")
        put_markdown(f"年龄: {data['age']}")
        put_markdown(f"标签: {data['tags']}")
        put_markdown(f"爱好: {data['loves']}")
        put_markdown(f"星座: {data['constellation']}")
        put_markdown(f"积目VIP: {'是' if data['vip'] == 1 else '否'}")
        put_markdown(f"关注数: {data['followCount']}")
        put_markdown(f"粉丝数: {data['fansCount']}")
        put_markdown(f"被喜欢: {data['likeMeCount']}")
        put_markdown(f"注册日期: {data['createTime']}")
        put_markdown(f"更新日期: {data['updateTime']}")
        put_markdown('# 封面：')
        display_images(data)
        # 显示完整的JSON数据
        put_json(data)
        put_markdown('如果你想要退出登录，可以点击下方的按钮  (·•᷄ࡇ•᷅ ）')
        put_buttons(['退出登录'], onclick=[logout])
        put_link('返回首页', '/')


def display_images(data):
    img_list = data.get('cover') or data.get('accountInfo').get('cover')
    table_data = []

    for i, img in enumerate(img_list):
        # 每行最多三个图片
        if i % 3 == 0:
            table_data.append([])

        # 显示图片
        img_url = img['url']
        img_tag = f'<img src="{img_url}" width="30%" onclick="window.open(\'{img_url}\', \'_blank\');" style="margin-right:10px; margin-bottom:10px;" />'
        table_data[-1].append(img_tag)

    put_html('<div style="display:flex; flex-wrap: wrap;">')
    for row in table_data:
        put_html('<div style="display:flex; flex-direction: row;">')
        for cell in row:
            put_html(cell)
        put_html('</div>')
    put_html('</div>')


def get_user_info(target_uid: int):
    try:
        # 检查demo
        if not demo_mode:
            sid = get_cookie('sid')
            uid = get_cookie('uid')
            if not sid or not uid:
                login()
        else:
            sid = demo_sid
            uid = demo_uid
        data = asyncio.run(jmc.get_user_info(target_uid, sid, uid))
        print(data)
        put_html('<hr>')
        # 显示账户信息
        display_account_data(data)
    except ValueError as e:
        with use_scope('account'):
            put_html('<hr>')
            put_markdown(f'获取用户信息失败！{e}')
            put_buttons(['重新登录'], onclick=[login])
            put_link('返回首页', '/')


@pywebio_config(theme='minty', title=title, description=description)
def about():
    # 修改footer
    session.run_js("""$('footer').remove()""")
    put_markdown(f'''
    ## 关于本项目
    - 本项目是一个基于积目APP的第三方客户端，使用Python语言编写，使用PyWebIO作为前后端框架，使用`JiMuAPI.py`作为后端API支持。
    - 本项目主要是方便各位开发者对积目APP的API进行学习和研究，同时也可以作为一个第三方客户端使用。
    - 本项目仅支持积目APP的部分功能，不支持积目APP的所有功能，更多功能正在开发中，欢迎提交PR。
    - 本项目仅供学习交流使用，不得用于非法用途，本项目的开发者不对使用本项目造成的任何后果负责。
    - 域名：[https://via-jimu.icu/](https://via-jimu.icu/) - `Via JiMu, I See You.`
    - GitHub：[Evil0ctal](https://github.com/Evil0ctal/)
    - 微信：Evil0ctal
    ## 项目地址
    - [https://github.com/Evil0ctal/JiMu-APP-Client](https://github.com/Evil0ctal/JiMu-APP-Client)
    ## 作者
    - [Evil0ctal](https://github.com/Evil0ctal)
    ## 版本
    - 当前版本：[`{version}`](https://github.com/Evil0ctal/JiMu-APP-Client/releases/)
    ## 功能
    ### V1.0
    - 支持登录积目账号(国家代码、手机号、密码)
    - 支持获取用户信息(账户信息、封面)
    ''')
    put_html('<hr>')
    put_link('返回首页', '/')


# 程序入口/Main interface
@pywebio_config(theme='minty', title=title, description=description)
def main():
    # 设置favicon
    logo_url = "https://raw.githubusercontent.com/Evil0ctal/JiMu-APP-Client/main/logo/logo.png"
    session.run_js(f"""
               $('#favicon32,#favicon16').remove(); 
               $('head').append('<link rel="icon" type="image/png" href={logo_url}>')
               """)
    # 修改footer
    session.run_js("""$('footer').remove()""")
    with use_scope('logo'):
        # 每次刷新页面都会重新回到顶部
        put_html('<br>')
        scroll_to('logo')
    # 顶部LOGO
    put_html(html=f"""
                    <p style="text-align: center;">
                        <img src={logo_url} alt="" width="100" height="100">
                    </p>
                    """)
    # 顶部标题
    put_markdown(f"""<div align='center' ><font size='6'>{title}</font></div>""")
    put_html('<hr>')
    put_row([put_link('首页', '/'),
             put_link('关于', '/about'),
             put_link('GitHub', 'https://github.com/Evil0ctal/JiMu-APP-Client', new_window=True),
             put_link('积目APP官网', 'https://www.hitup.cn', new_window=True),
             ])
    # 要求用户输入选择
    options = ['注册', '登录', '登出', '查询本人信息', '查询他人信息', '用户上线通知', '用户账号分析', '批量喜欢附近的人', '修改账号位置', '接入ChatGPT自动聊天']
    select_options = select('请选择一个选项以继续', required=True,
                            options=options,
                            help_text='📎选上面的选项然后点击提交')
    # 注册
    if select_options == options[0]:
        register()
    # 登录
    if select_options == options[1]:
        # 检查演示模式
        if demo_mode:
            demo_mode_notification()
        else:
            login()
    # 登出
    elif select_options == options[2]:
        # 检查演示模式
        if demo_mode:
            demo_mode_notification()
        else:
            logout()
    # 查询本人信息
    elif select_options == options[3]:
        get_user_info(demo_uid)
    # 查询他人信息
    elif select_options == options[4]:
        target_uid = input('请输入要查询的用户UID', type=NUMBER, required=True,
                           help_text='📎输入一个数字然后点击提交，积目APP上在个人主页右上角可以找到用户ID。',
                           placeholder='1234567')
        get_user_info(target_uid)
    # 监控用户上线时间
    elif select_options == options[5]:
        # monitor_online_time()
        put_markdown('该功能正在开发中，敬请期待！')
    # 用户账号分析
    elif select_options == options[6]:
        # user_account_analysis()
        put_markdown('该功能正在开发中，敬请期待！')
    # 批量喜欢附近的人
    elif select_options == options[7]:
        # batch_like_nearby_users()
        put_markdown('该功能正在开发中，敬请期待！')
    # 修改账号位置
    elif select_options == options[8]:
        # change_account_location()
        put_markdown('该功能正在开发中，敬请期待！')
    # 接入ChatGPT自动聊天
    elif select_options == options[9]:
        # chat_gpt()
        put_markdown('该功能正在开发中，敬请期待！')


if __name__ == '__main__':
    port = int(webapp_config['port'])
    host = webapp_config['host']
    # 使用PyWebIO启动网页APP
    # start_server(main, port=port, host=host, debug=True)

    # 使用Flask启动网页APP
    app.add_url_rule('/', 'root', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])
    app.add_url_rule('/about', 'about', webio_view(about), methods=['GET', 'POST', 'OPTIONS'])
    app.run(host=host, port=port)
