from aip import AipNlp
import urllib.request,time,ssl,json,string
import cv2,time
import threading,io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import socket

#请自行在百度ai注册申请
APP_ID="*****"
API_KEY="******"
SECRET_KEY="*****"
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

# 获取 token
def gettoken():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_KEY + '&client_secret=' + SECRET_KEY
    request = urllib.request.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    content = response.read()
    if (content):
        #print(type(content))#<class 'bytes'>
        pass
    content_str=str(content, encoding="utf-8")
    ###eval将字符串转换成字典
    content_dir = eval(content_str)
    access_token = content_dir['access_token']
    return access_token


# 调用百度 AI 智能春联接口（用于测试）
def get_couplets(text, token_key, index=0):
    """
    调用百度AI智能春联接口，并生成横批、上联和下联
    :param text: 智能春联的主题（官方限制不超过5个字）
    :param token_key: 通过调用 get_token_key() 获取的 token
    :param index: 不同的 index 会生成不同的春联
    :return: 调用智能春联生成的数据
    """
    request_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/couplets'
    params_d = dict()
    params_d['text'] = text
    params_d['index'] = index
    params = json.dumps(params_d).encode('utf-8')
    access_token = token_key
    request_url = request_url + "?access_token=" + access_token
    request = urllib.request.Request(url=request_url, data=params)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request)
    content = response.read()
    if content:
        data = json.loads(content)
        if "error_msg" in data.keys():
            return text
        else:
            return data


# 解析生成的春联
def parse_couplets(data):
    """
    解析调用智能春联生成的数据
    :param data: 调用智能春联生成的有效数据
    :return: 横批（center）、上联（first）和下联（second）
    """
    center = data['couplets']['center']
    first = data['couplets']['first']
    second = data['couplets']['second']
    print(f'上联：{first}')
    print(f'下联：{second}')
    print(f'横批：{center}')
    return center, first, second

# 调用百度 AI 智能写诗接口（用于测试）
def get_poem(text, token_key, index=0):
    """
    调用百度AI智能写诗接口，并生成七言诗
    :param text: 智能写诗的主题（官方限制不超过5个字）
    :param token_key: 通过调用 get_token_key() 获取的 token
    :param index: 不同的 index 会生成不同的七言诗
    :return: 调用智能写诗生成的数据
    """
    request_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/poem'
    params_d = dict()
    params_d['text'] = text
    params_d['index'] = index
    params = json.dumps(params_d).encode('utf-8')
    access_token = token_key
    request_url = request_url + "?access_token=" + access_token
    request = urllib.request.Request(url=request_url, data=params)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request)
    content = response.read()
    if content:
        data = json.loads(content)
        #print(data)
        if "error_msg" in data.keys():
            return text
        else:
            return data


# 解析生成的诗句
def parse_poem(data):
    """
    解析调用智能写诗生成的数据
    :param data: 调用智能写诗生成的有效数据
    :return: 诗的题目（title）和诗的内容（content）
    """
    title = data['poem'][0]['title']
    poem = data['poem'][0]['content'].replace('\t', '\n')
    print(title)
    print(poem)
    return title, poem

#返回矩形(备用)
def getrect(fimg):
    image = cv2.imread(fimg)
    blur = cv2.pyrMeanShiftFiltering(image, 11, 21)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
        if len(approx) == 4:
            x,y,w,h = cv2.boundingRect(approx)
            #x,y,w,h = cv2.minAreaRect(approx)
            #print(approx)
            if abs(w-h)>5:
                cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
                
    #cv2.imshow('thresh', thresh)
    cv2.imshow('image', image)
    cv2.waitKey()
    

def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype("simhei.ttf", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def zh_ch(string):
    return string.encode("gbk").decode(errors="ignore")

text=input("请输入关键词（不超过5个字）：")
couplets=get_couplets(text, gettoken(), index=0)
if couplets!=text:
    ckey=parse_couplets(couplets)

poem=get_poem(text, gettoken(), index=0)
if poem!=text:
    pkey=parse_poem(poem)

img=cv2.imread("bg.jpg")
img2=cv2.imread("bg1.jpg")
#cv2.imshow("img",img)
img=cv2ImgAddText(img, ckey[0], 135, 35, (0, 0, 0), 30)
for i in ckey[1]:
    img=cv2ImgAddText(img, i, 48, 70+ckey[1].index(i)*45, (0, 0, 0), 30)
for i in ckey[2]:
    img=cv2ImgAddText(img, i,328, 70+ckey[2].index(i)*45, (0, 0, 0), 30)

img2=cv2ImgAddText(img2, pkey[0], 320, 100, (0, 0, 0), 30)
img2=cv2ImgAddText(img2, pkey[1], 240, 150, (0, 0, 0), 30)

cv2.imshow(zh_ch(text),img)
cv2.imshow(zh_ch("诗"),img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
