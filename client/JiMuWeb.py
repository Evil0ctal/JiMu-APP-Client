from pywebio import *
from pywebio import config as pywebio_config
from pywebio.input import *
from pywebio.output import *
from pywebio.session import info as session_info, run_asyncio_coroutine
from api.JiMuClient import JiMuClient
import asyncio

jmc = JiMuClient()


# 程序入口/Main interface
@pywebio_config(theme='minty', title='积目APP网页客户端', description='网页版积目APP，基于PyWebIO构建。')
async def main():
    # 设置favicon
    favicon_url = "./logo.png"
    session.run_js("""
               $('#favicon32,#favicon16').remove(); 
               $('head').append('<link rel="icon" type="image/png" href="%s">')
               """ % favicon_url)
    tittle = "积目APP网页客户端"
    version = "V1.0"
    put_markdown(f"""<div align='center' ><font size='6'>{tittle}-{version}</font></div>""")
    put_html('<hr>')
    put_markdown("`Via JiMu, I See You.`")
    put_markdown("[https://via-jimu.icu/](https://via-jimu.icu/)")


if __name__ == '__main__':
    start_server(main, port=80, host='127.0.0.1', debug=False)
