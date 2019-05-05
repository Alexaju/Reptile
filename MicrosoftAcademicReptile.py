import requests
import json
import pandas as pd
import numpy as np
import time
requests.packages.urllib3.disable_warnings()

Nation = pd.read_csv("NATION.csv")

AN = pd.read_csv("AN.csv")
AA = pd.read_csv("author2.csv")

def clearup(text,head):
    l = len(text)
    if l <=5:
        ct = [None] * l
        yr = [None] * l
        for i in range(l):
            ct[i] = text[i]['count']
            yr[i] = head + str(text[i]['year'])

    else:
        temp = text[l - 6:]
        ct = [None] * 5
        yr = [None] * 5
        for i in range(5):
            ct[i] = temp[i]['count']
            yr[i] = head+str(temp[i]['year'])
    return pd.DataFrame([ct], columns=yr)

def postsearch(url,page,filt):
    payloadData = {
         "query":"artificial intelligence",
         "queryExpression":"@@@Composite(F.FN=='artificial intelligence')",
        "filters":filt,
         "orderBy":0,
         "skip":page,
         "sortAscending":'true',
         "take":10}

    payloadHeader = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'host' : 'academic.microsoft.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    res = ''
    while res=='':

        try:
            res = requests.post(url, json=payloadData, headers=payloadHeader, verify=False,timeout=10)
        except:
            print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    content = res.json()
    return content

def CountrySearch(ID):

    u = 'https://academic.microsoft.com/api/entity/'
    link = u + str(ID)+ '?entityType=6'
    header = {'accept': 'application/json',
        #'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    res = ''
    while res == '':
        try:
            res = requests.get(url=link,headers=header, verify=False,timeout=10)
        except:
            print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    globals = {
        'true': 0,
        'false': 1
    }
    if len(res.text)==0:
        return 'NA',0
    try:
        content = eval(res.text,globals)['entity']
    except:
        return 'NA',0

    des = content['description']

    nation = ' '

    for i in range(len(Nation)):
        count=0
        if Nation['nation'][i] in des or Nation['nationality'][i] in des:
            if count>1:
                nation = des
                break
            nation = Nation['nation'][i]
            count = count + 1
            continue

    for i in range(len(nation)):
        for j in range(len(AN['A'])):
            if nation[i] == AN['A'][j]:
                nation[i] = AN['N'][j]
                break


    if len(nation) == 1:
        return des
    return nation

def author1nd(df):
    u = 'https://academic.microsoft.com/api/entity/author/'
    header = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'host' : 'academic.microsoft.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86  Safari/537.36'
    }

    paperid = df['paperResult']['id']
    authorid = df['paperResult']['authors'][0]['id']
    link = u + str(authorid) + '?paperId=' + str(paperid)

    res = ''
    while res == '' or len(res.text)<2:
        try:
            res = requests.get(url=link, headers=header, verify=False,timeout=10)
        except:
            print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    globals = {
        'true': 0,
        'false': 1
    }
    content = eval(res.text, globals)['entity']

    Total = pd.DataFrame({'FirstPub':[content['publicationCount']],'FirstCite': [content['citationCnt']]})

    YearlyPub = clearup(content['publicationCountByYear'],'pub')
    YearlyCite = clearup(content['citationCountByYear'],'cite')
    byear = pd.concat((YearlyCite,YearlyPub),axis=1,ignore_index=False,sort=True)
    return Total,byear

def authors(df):
    authorlist = df['paperResult']['authors']
    FirstAuthor = df['paperResult']['authors'][0]
    l = len(df['paperResult']['authors'])
    country = ['NA'] * l

    for i in range(l):
        if ifna('displayName',authorlist[i]['currentInstitution']):
            continue
        else:
            if ifna('id',authorlist[i]['currentInstitution']):
                country[i] = authorlist[i]['currentInstitution']['displayName']
                for i in range(len(AN)):
                    if country[i] == AN['A'][i]:
                        country[i] = AN['N'][i]
                        break

            else:
                time.sleep(1)
                id = authorlist[i]['currentInstitution']['id']
                country[i]= CountrySearch(id)
                if country[i]=='NA':
                    for i in range(len(AA)):
                        if authorlist[i]['diaplayName'] == AA['A'][i]:
                            country[i] = AA['N'][i]
                            break



    if ifna('displayName',FirstAuthor):
        FirstA = 'NA'
    else:
        FirstA = FirstAuthor['displayName']


    if ifna('id', FirstAuthor['currentInstitution']):
        FirstIns=FirstAuthor['currentInstitution']['displayName']
        FirstNation= 'NA'
        for i in range(len(AA)):
            if FirstA == AA['A'][i]:
                FirstNation = AA['N'][i]
                break
        for i in range(len(AN)):
            if FirstIns == AN['A'][i]:
                FirstNation = AN['N'][i]
                break
    else:
        if ifna('displayName', FirstAuthor['currentInstitution']):
            try:
                F = df['paperResult']['authors'][1]
                FirstIns = F['currentInstitution']['displayName']
                FirstNation =CountrySearch(F['currentInstitution']['id'])
                for i in range(len(AN)):
                    if FirstIns == AN['A'][i]:
                        FirstNation = AN['N'][i]
                        break
            except:
                FirstIns ='NA'
                FirstNation = 'NA'

            if FirstNation == 'NA' :
                for i in range(len(AA)):
                    if FirstA == AA['A'][i]:
                        FirstNation = AA['N'][i]
                        break

        else:
            FirstIns = FirstAuthor['currentInstitution']['displayName']
            insID = FirstAuthor['currentInstitution']['id']
            try:
                FirstNation = CountrySearch(insID)
                for i in range(len(AN)):
                    if FirstIns == AN['A'][i]:
                        FirstNation = AN['N'][i]
                        break
            except:
                FirstNation='NA'



    N = {}
    for j in country:
        N[j] = country.count(j)
    Nations = pd.DataFrame([list(N.values())], columns=list(N.keys()))
    info = pd.DataFrame({'FirstAuthor':[FirstA],
                         'FirstIns':[FirstIns],
                         'FirstNation': [FirstNation],
                         'Num_authors':[l]})
    return info,Nations

def ifna(name,ele):
    if name in list(ele.keys()):
        return False
    else:
        return True

def getinfo(content):
    numByear = pd.DataFrame({'T': [10000000]})
    Nations = pd.DataFrame({'T': ['aaaaa']})
    Head = pd.DataFrame({'T': ['A']})
    for j in range(len(content['paperResults'])):
        df = pd.DataFrame(content['paperResults'][j])
        time.sleep(1)
        Total,Byear = author1nd(df)
        PubDate = df['paperResult']['venueInfo']['publishedDate'][0:4]
        Journal = df['paperResult']['venueInfo']['displayName']
        Author, N = authors(df)

        if ifna('citationCnt',df['paperResult']):
            Citation = -1
        else:
            Citation = df['paperResult']['citationCnt']
            if ifna('displayName',df['paperResult']):
                Title = None
            else:
                Title = df['paperResult']['displayName']
        Info = pd.DataFrame({'Journal':[Journal],'Title':[Title],'PubYear':[PubDate],'Citation':[Citation]})
        numByear = pd.concat((numByear,Byear),axis=0,ignore_index=True, sort=True)
        Nations = pd.concat((Nations,N),axis=0,ignore_index=True,sort=True)
        Info = pd.concat((Info,Total,Author), axis=1,sort=False)
        Head = pd.concat((Head,Info), axis=0,ignore_index=True, sort=False)

    Head.drop('T',inplace=True,axis=1)
    numByear.drop('T', inplace=True,axis=1)
    Nations.drop('T', inplace=True,axis=1)

    return Head,Nations,numByear

def scrap(end,conf):
    if conf =="AAAI":
        confilter=["Pt='3'", "Composite(F.FId=154945302)", "Composite(C.CId=1184914352)", "Y>=2015"]
    if conf == "ECCV":
        confilter=["Pt='3'","Composite(F.FId=154945302)","Composite(C.CId=1124077590)","Y>=2015"]
    if conf=="ICML":
        confilter =["Pt='3'", "Composite(F.FId=154945302)", "Composite(C.CId=1180662882)", "Y>=2015"]
    if conf =="CVPR":
        confilter =["Pt='3'","Composite(F.FId=154945302)","Composite(C.CId=1158167855)","Y>=2015"]

    if conf == "ICLR":
        confilter =["Pt='3'", "Composite(F.FId=154945302)","Composite(C.CId=2584161585)", "Y>=2015"]
    if conf == "NIPS":
        confilter=["Pt='3'", "Composite(F.FId=154945302)", "Composite(C.CId=1127325140)", "Y>=2016"]

    url = 'https://academic.microsoft.com/api/search'

    head = pd.DataFrame({'kk':['A']})
    nation = pd.DataFrame({'cc':['vv']})
    numbyear = pd.DataFrame({'pub':[0000]})

    count = 1
    num = 17
    for series in range(end):
        time.sleep(1)
        for i in range(num*series,num*(series+1)):
            time.sleep(1)
            page = i*10
            content = postsearch(url,page,confilter)
            Head, Nations, numByear = getinfo(content)
            head = pd.concat((head,Head),axis=0,ignore_index=True,sort=False)
            nation = pd.concat((nation,Nations),axis=0,ignore_index=True,sort=True)
            numbyear = pd.concat((numbyear,numByear),axis=0,ignore_index=True,sort=True)
            print(i+1)

    head.drop('kk',inplace=True,axis=1)
    numbyear.drop('pub',inplace=True,axis=1)
    nation.drop('cc',inplace=True,axis=1)
    numbyear = numbyear[['cite2014','cite2015','cite2016','cite2017','cite2018','cite2019',
                         'pub2013','pub2014', 'pub2015', 'pub2016', 'pub2017', 'pub2018', 'pub2019']]

    head = pd.concat((head,numbyear),axis=1,sort=None)
    headname = conf+"_head.csv"
    nationname = conf+"_nation.csv"
    yearname = conf+"_year.csv"

    head.to_csv(headname, header=True)
    nation.to_csv(nationname, header=True)
    numbyear.to_csv(yearname, header=True)

