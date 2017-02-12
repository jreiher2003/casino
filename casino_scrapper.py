import os
import itertools
import requests 
from collections import OrderedDict 
import pymongo 
from pymongo import MongoClient 
from bs4 import BeautifulSoup as bs 
from pprint import pprint

 
gwages_login = "https://www.gwages.com/login.php/"
gwages_login_redirect = "https://www.gwages.com/login-process.php/"
gwages_url = "https://www.gwages.com/marketing-tools.php"
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

def connect_gwages(username, password):
    """ 
    takes a username, password connects to gwages login passes all necessary params 
    and returns a active session to connect to protected pages 
    """
    url = gwages_login
    with requests.Session() as s:
        headers = {'user-agent': user_agent,"referer": url}
        g = s.get(url, headers=headers)
        csrf_token = g.cookies['CSRFtoken']
        payload = {"username": username,"password": password,'login':'Login','CSRFtoken':csrf_token}
        r = s.post(gwages_login_redirect, data=payload, headers=headers)
        return s

def find_length_of_pages(s, casino, platform):
    """ 
    Finds number of pages based on casino and platform 
    scrapes bottom of page by platform and returns the total number of results by casino and platform
    """
    content = s.get(gwages_url + "?asset_casino_id=%s&platform_id=%s&page=" %  (casino, platform))
    soup = bs(content.text, "html.parser")
    results = soup.find("span",class_="pull-left text-muted results-counter")
    if results != None:
        return results.text.split()[3]

def update_get_all_casinos(s, gwages_dic, platform):
    """ 
    Creates a list of results based on platform and casino id.
    """
    all_lens = []
    for i in gwages_dic:
        all_lens.append(find_length_of_pages(s, i.values()[0], platform))
    return all_lens 

def get_all_casinos(s):
    """ 
    Creates list of dicts of all casinos and their id  [{id:value,name:casino},{...}]
    A dict to iterate on and add to later  
    """
    gwages = []
    content = s.get(gwages_url)
    soup = bs(content.text, "html.parser")
    casinos = soup.find(id='casino_dd')
    for c in casinos.find_all('option'):
        if c.text != 'All':
            gwages.append({'id':c['value'],'name':c.text})
    return gwages


def num_pages(num):
    """
    a function that returns the ceil of results_destop/10 and results_mobile/10
    as the num of pages to iterate in pop_casino_links function. guard against 
    results that are None, less than 10
    """
    import math 
    if num == None:return 1
    num = int(num)
    if num <= 10:return 1
    return int(str(math.ceil(num/10.0)).split(".")[0])

def put_results_in_dic(s):
    desktop1 = "1"
    mobile2 = "2"
    gwages_dic = get_all_casinos(s)
    results_list_desktop = update_get_all_casinos(s, gwages_dic, desktop1)
    results_list_mobile = update_get_all_casinos(s, gwages_dic, mobile2)
    for d,num in zip(gwages_dic,results_list_desktop):
        d['results_desktop'] = num
    for m,num1 in zip(gwages_dic,results_list_mobile):
        m["results_mobile"] = num1 
    for i in gwages_dic:
        i['mobile'] = []
        i['desktop'] = []
    # print gwages_dic 
    db.insert(gwages_dic)
    conn.close()
    return gwages_dic

########################################################################
## bottom four functions update desktop: [], and mobile: [] fields in doc

def pop_casino_links(s, casino, platform, page):
    """ filter url requests by casino id, desktop or mobile 
    then find the table and scrapes links 
    returns a list 
    """
    link = []
    content = s.get(gwages_url+"?asset_casino_id=%s&platform_id=%s&page=%s" %  (casino, platform, page))
    soup = bs(content.text, "html.parser")
   
    tables = soup.find_all("table")
    last_table_index = int((len(tables)-1))
    try:  
        table = soup.find_all("table")[last_table_index]
        headers = [th.text for th in table.find_all('th')]
        headers.append("Code/Link")
        
        contents = [td.text for td in table.find_all('td')]
        contents_tup = [tuple(contents[i:i+6]) for i in range(0,len(contents), 6)]
        links = [str(tx.a) if tx.a else tx.text for tx in table.find_all('textarea')]
        
        new_list = [x+(y,) for x,y in zip(contents_tup,links)]
        data = [dict(itertools.izip(headers, values)) for values in new_list]
        # remove unneccasary key,value pairs
        for i in data:
            del i['Preview']
            del i['Link/Code']
        return data 
    except IndexError:
        return []

def _mobile(gwages_dic, casino_id):
    """
    gwages_dic is the returned dic from put_results_in_dic()
     returns list of links by casino id and platform 
    i.values()[4] is the total number of MOBILE results
    """
    mobile1 = []
    for i in gwages_dic:
        if i['id'] == casino_id:
            print "num_pages ", num_pages(i.values()[4])
            for page in range(1,num_pages(i.values()[4])+1):
                print "################## mobile ", page, " casino_id ", casino_id
                if page == None:
                    mobile1 += pop_casino_links(s, casino_id, mobile2, "1")
                mobile1 += pop_casino_links(s, casino_id, mobile2, page)
    return mobile1

def _desktop(gwages_dic, casino_id):
    """
    gwages_dic is the returned dic from put_results_in_dic()
     returns list of links by casino id and platform 
    i.values()[3] is the total number of DESKTOP results
    """
    desktop = []
    for i in gwages_dic:
        if i['id'] == casino_id:
            print "num_pages ", num_pages(i.values()[3])
            for page in range(1,num_pages(i.values()[3])+1):
                print "################## desktop ", page, " casino_id ", casino_id
                if page == None:
                    desktop += pop_casino_links(s, casino_id, desktop1, "1")
                desktop += pop_casino_links(s, casino_id, desktop1, page)
    return desktop

def update_gwages_mongo(casino_id):
    """ 
    connect to db finds doc by casino id, updates doc by platform by passing a function _desktop or _mobile which 
    returns a list.  closes connection.
    """
    db = conn.casino.gwages
    gwages_dic_d_dreams = _desktop(gwages_dic, casino_id)
    gwages_dic_m_dreams = _mobile(gwages_dic, casino_id)
    db.update({'id': casino_id}, {"$set":{"desktop": gwages_dic_d_dreams}}, upsert=True)
    db.update({'id': casino_id}, {"$set":{'mobile': gwages_dic_m_dreams}}, upsert=True)
    conn.close()
    

if __name__ == "__main__":
    conn = MongoClient(os.environ['MONGO_DB'])
    db = conn.casino.gwages
    db.drop()
    conn.close()
    db = conn.casino.gwages
    
    s = connect_gwages(os.environ['GWAGES_USERNAME'], os.environ["GWAGES_PASSWORD"])
    desktop1 = "1"
    mobile2 = "2"
    # passes in update_gwages_mongo --> _desktop() or _mobile()
    gwages_dic = put_results_in_dic(s)
    #Dreams 6
    update_gwages_mongo("6")
    # # CoolCat 7
    update_gwages_mongo("7")
    # ClubPlayer 9
    update_gwages_mongo("9")
    # # PalaceOfChange 10
    update_gwages_mongo("10")
    # # WildVegas 11
    update_gwages_mongo("11")
    # # # RubySlots 13
    update_gwages_mongo("13")
    # # # Prism 14
    update_gwages_mongo("14")
    # SlotsOfVegas 15
    update_gwages_mongo("15")
    # # BingoKnights 17
    update_gwages_mongo("17")
    # 123Bingoonline 22
    update_gwages_mongo("22")
    


        


   