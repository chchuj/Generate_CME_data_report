# -- coding:utf-8 --
# author:ZhaoKangming
# 功能：爬虫之模拟登录华医网CME

import requests
import os
from aip import AipOcr
from PIL import Image
import sys
# from bs4 import BeautifulSoup
# import shutil


# 定义公共变量
script_path: str = os.path.dirname(os.path.realpath(__file__))
checkbox_gif_path: str = os.path.join(script_path, 'cb_pic.gif')
checkbox_png_path: str = os.path.join(script_path, 'cb_pic.png')


def get_checkbox_pic() -> list:
    """
    【功能】在华医CME网站上获取验证码图片
    """
    url = "https://cme3.91huayi.com/secure/CheckCode.aspx"
    headers = {'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'}

    session = requests.Session()
    response = session.get(url, headers=headers)
    session_id: str = session.cookies.get_dict()['ASP.NET_SessionId']

    if os.path.exists(checkbox_gif_path):
        os.remove(checkbox_gif_path)

    with open(checkbox_gif_path, 'wb') as cb_pic:
        cb_pic.write(response.content)

    return [response.status_code, session_id]


def gif_to_png():
    """
    【功能】将储存下来的gif转化为png图片
    """
    im = Image.open(checkbox_gif_path)  # 使用Image模块的open()方法打开gif动态图像时，默认是第一帧
    im.tell()
    if os.path.exists(checkbox_png_path):
        os.remove(checkbox_png_path)
    im.save(checkbox_png_path)
    # print('处理完成')

    return None


def baidu_ocr_pic(pic_path: str) -> str:
    """
    【功能】识别验证码中的文本
    """
    # 填写百度AIP相关信息构建客户端
    APP_ID = ''  # 百度API SECRET_KEY
    API_KEY = ''  # 百度API SECRET_KEY
    SECRET_KEY = ''  # 百度API SECRET_KEY
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    with open(pic_path, 'rb') as pic:
        ocr_result = client.numbers(pic.read())  # 调用数字识别
        try:
            ocr_words: str = ocr_result['words_result'][0]['words']
            # print(ocr_words)
        except KeyError:
            print(ocr_result)
            ocr_words: str = str(ocr_result)
            sys.exit()

    return ocr_words


def login_huayi_cme(seesion_id: str, check_code: str) -> dict:
    """
    【功能】模拟登陆华医网CME
    """
    huayi_account: str = '' # 你的华医网账号
    huayi_psw: str = '' # 你的华医网密码
    url = f"https://cme3.91huayi.com/ashx/loginJson.ashx?UserName={huayi_account}&Password={huayi_psw}&loginType=1&ScreenX=1920&ScreenY=1080&code={check_code}"
    cookies: dict = {'ASP.NET_SessionId': seesion_id}
    response = requests.post(url, cookies=cookies)

    # print(list(response.json()))

    return list(response.json())[0]


def get_course_info(course_name: str):
    """
    【功能】从CME课程情况中获取课程的信息
    """
    pass


def main():
    """
    【功能】整合调取程序
    """
    ok_login: bool = False
    # 尝试三次登录，三次都失败后退出
    for i in range(3):
        get_gif_result: list = get_checkbox_pic()
        if get_gif_result[0] == 200:
            gif_to_png()
            ocr_words: str = baidu_ocr_pic(checkbox_png_path)
            if len(ocr_words) == 5:
                login_result_list: dict = login_huayi_cme(get_gif_result[1], ocr_words)
                if not login_result_list['provinceID'] == '':
                    ok_login = True
                    print('【模拟登录】登陆成功！' + str(login_result_list))
                    break
            else:
                print(f'Try:{i} --【识别验证码】识别位数错误')
        else:
            print(f'Try:{i} --【下载验证码】下载失败，状态码为 {get_gif_result[0]}')

    if ok_login == True:
        pass


main()
