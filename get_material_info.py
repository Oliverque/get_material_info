#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      fu
#
# Created:     11/02/2020
# Copyright:   (c) fu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import random
import time
import re
import pandas as pd
from  requests import get
from urllib import parse
from bs4 import BeautifulSoup as bf

'''请求头函数'''

def agent():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.42 Safari/537.36',
        'Cookie':'_ga=GA1.2.1669274313.1581578187; _gid=GA1.2.101545613.1581578187; JSESSIONID=E54E87534E685F4AF2F925B37ED7ADE8; Hm_lvt_f121c3ffd570499b9229f30828cb0d5f=1581578187,1581578762,1581581215,1581594168; Hm_lpvt_f121c3ffd570499b9229f30828cb0d5f=1581594214',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.chemsrc.com',
        'Referer': 'https://www.chemsrc.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    return headers

'''调整名字信息格式'''
def parse_info(strings):
    split_list= []

    info_list = strings.split(':')
    for item in info_list:
        if '分' in item :
           item=item.replace('分',':分')
        if '：'in item:
           sub_list =item.split('：')
           for i in sub_list:
               split_list.append(i)
        else:
            split_list.append(item)
   # print('信息调整返回正常')
    return split_list
'''取出字符串中的数字'''
def get_number(strings):
    if strings =='N/A':
       return 'N/A'
    else:
       if 'ºC' in strings :
           number = strings.split('ºC')[0]
           new_strings=re.findall(r'[1-9]+\.?[0-9]*',number)[0]
           return new_strings
       if 'g' in strings:
           number = strings.split('g/')[0]
           new_strings=re.findall(r'[1-9]+\.?[0-9]*',number)[0]
           return new_strings
       if 'g/cm3' in strings:
           number = strings.split('g/cm3')[0]
           new_strings=re.findall(r'[1-9]+\.?[0-9]*',number)[0]
           return new_strings
       else:
            new_strings=re.findall(r'[1-9]+\.?[0-9]*',strings)[0]
            return new_strings
'''输出名字信息字典'''
def parse_name_info_dict(split_list):
    split_dict={}
     #print(split_list)
    split_dict['name']=split_list[0]
    split_dict['English_name']=split_list[2]
    split_dict['CAS号']=split_list[5].split(':')[0]
    split_dict['分子式']=split_list[6]
    #print('名字信息返回正常')
    return split_dict

'''输出物理信息字典'''
def parse_phy_info_dict(split_list):
    split_dict={}
     #print(split_list)
    split_dict['分子量']=split_list[1]
    split_dict['密度']=get_number(split_list[3])
    split_dict['沸点']=get_number(split_list[5])
    split_dict['熔点']=get_number(split_list[7])
    #print('物理信息返回正常')
    return split_dict

#整理其中不合格的格式
def parse_phy_info(strings,parse_dict):
    strings = ''.join(strings.split())
    for be_replaced_name,repace_name in zip(parse_dict['be_replaced_list'],parse_dict['replace_list']):
        strings=strings.replace(be_replaced_name,repace_name)

    #print('信息整理返回正常')
    return strings


def replace_data():

    parse_dict ={
        'be_replaced_list':['密','沸','熔'],
        'replace_list':['：密','：沸','：熔']
    }
    #print('替换返回正常')
    return parse_dict
def download_struct_img(url,name):

    response = get(url).content
    with open('structure_img\\'+name+'.png','ab') as img_file:
         img_file.write(response)

'''解析网页数据'''

def parse_html(url,material_name):
    try:
        resp = get(url, headers=agent())
        # 将编码方式设置为从内容中分析出的响应内容编码方式
        if resp.status_code == 200:
           # 定位获取表格信息
           table = bf(resp.content.decode('utf-8'),'lxml').select('.rowDat')
           info_list=[]
           for item in table:
               try:
                   if material_name == item.select('td')[1].select('a')[0].text.strip():
                      #print('进入选择名称选择项')
                      info_dict ={}
                      info_dict['结构图名称']=item.select('td')[0].select('img')[0]['alt']
                      #print(info_dict['结构图名称'])
                      info_dict['结构图地址']=item.select('td')[0].select('img')[0]['data-original']
                      #下载结构图
                      download_struct_img(info_dict['结构图地址'],info_dict['结构图名称'])
                      info_dict['名称']= item.select('td')[1].select('a')[0].text
                      #print('进入选择网址选项')
                      info_dict['url'] = 'https://www.chemsrc.com'+item.select('td')[1].select('a')[0]['href']
                      name_info= item.select('td')[1].text.replace('\n','\t').replace('\t','').replace('\r',':')
                      #print(name_info)
                      sup_info_dict=parse_name_info_dict(parse_info(name_info))

                      info_dict['English_name']=sup_info_dict['English_name']
                      info_dict['CAS号']=sup_info_dict['CAS号']
                      info_dict['分子式']=sup_info_dict['分子式']
                      phy_info= item.select('td')[2].text

                      phy_data = parse_phy_info_dict(parse_info(parse_phy_info(phy_info,replace_data())))
                      info_dict['分子量']=phy_data['分子量']
                      info_dict['密度']=phy_data['密度']
                      info_dict['沸点']=phy_data['沸点']
                      info_dict['熔点']=phy_data['熔点']
                      info_list.append(info_dict)
                      #print('已经找到的药品是：'+m_name)
                   else:
                        if len(info_list)==0 and table.index(item)== len(table)-1:
                           print('没有找到{}，请重新输入'.format(material_name))
                           return None
               except Exception as e:
                      print(e)
           return info_list
        else:
            print('爬取失败，没有找到{}，请重新输入检索'.format(material_name))
    except Exception as e:
        print('爬取失败，没有找到{}，请重新输入检索'.format(material_name))
        print(e)

def get_data(material_name):
    url = 'https://www.chemsrc.com/searchResult/'+'%25'.join(tuple(parse.quote(material_name,encoding='utf-8').split('%')))+'/'

    table = parse_html(url,material_name)

    return table


def parse_data(inspect_material_list):
    data_list = []

    for item in inspect_material_list:
        item = item.strip()
        print('正在下载'+item+'的数据')
        data_info = get_data(item)
        try:
            for i in data_info:
                data_list.append(i)
            time.sleep(4)
        except:
            continue

    return data_list

def export_excel(export):

   pf = pd.DataFrame(export)
   pf.to_csv('LATP.csv',index=False,columns=['名称','分子式','CAS号','分子量','密度','沸点','熔点'])
   print('Done')

if __name__ == '__main__':
    with open('material_name.txt','r',encoding='utf-8') as m_file:
         inspect_material_list = m_file.readlines()

    data_list = parse_data(inspect_material_list)
    export_excel(data_list)

