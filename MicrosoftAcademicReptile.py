import requests
import json
import pandas as pd
import time
requests.packages.urllib3.disable_warnings()

Nation = pd.read_csv("NATION.csv") # Nations and nationality file for string comparison#

################################################
def ifna(name,ele):
    if name in list(ele.keys()):
        return False
    else:
        return True

def ifeduc(des):
    univ = ['university','University','universities','institute','organization','institution','Academy','research laboratories','laboratory','academy']
    for i in range(len(univ)):
        if univ[i] in [des]:
            return 1

    return 0


def databyYear(text,head):
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

def getField(df):
    fieldslist = df['paperResult']['fieldsOfStudy']
    l = len(fieldslist)
    Fields = ""
    for i in range(l):
        if not ('displayName' in list(fieldslist[i].keys())):
            Fields = Fields + 'nan'+ ','
        else:
            Fields = Fields + fieldslist[i]['displayName'] + ','
    return Fields
    
###############################################

def postsearch(url,page):
    payloadData = {"query":"artificial intelligence",
                   "queryExpression":"@@@Composite(F.FN=='artificial intelligence')",
                   #"filters":["Pt='3'","Composite(F.FId=154945302)","Composite(C.CId=1158167855)","Y>=2015"],
                   #"filters": ["Pt='3'", "Composite(F.FId=154945302)","Composite(C.CId=2584161585)", "Y>=2015"],
                   #"filters":["Pt='3'", "Composite(F.FId=154945302)", "Composite(C.CId=1184914352)", "Y>=2015"],
                   "filters": ["Pt='3'", "Composite(F.FId=154945302)", "Composite(C.CId=1180662882)", "Y>=2015"],
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
            res = requests.post(url, json=payloadData, headers=payloadHeader, verify=False)
        except:
            print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    content = res.json()
    return content



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
    while res == '':

        try:
            res = requests.get(url=link, headers=header, verify=False)
        except:
            print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    globals = {
        'true': 0,
        'false': 1
    }
    content = eval(res.text, globals)['entity']

    TotalPub = pd.DataFrame({'TotalPub':[content['publicationCount']]})
    TotalCit = pd.DataFrame({'TotalCite': [content['citationCnt']]})
    Total = pd.concat((TotalPub,TotalCit),axis=1,ignore_index=True)

    YearlyPub = databyYear(content['publicationCountByYear'],'pub')
    YearlyCite = databyYear(content['citationCountByYear'],'cite')
    byear = pd.concat((YearlyCite,YearlyPub),axis=1,ignore_index=False,sort=True)
    return Total,byear


def CountrySearch(ID):

    u = 'https://academic.microsoft.com/api/entity/'
    link = u + str(ID)+ '?entityType=6'
    header = {'accept': 'application/json',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    res = ''
    while res == '':
        try:
            res = requests.get(url=link,headers=header, verify=False)
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
        
    content = eval(res.text,globals)['entity']
    des = content['description']

    num_educ = ifeduc(des)
    nation = ' '
    for i in range(len(Nation)):

        if Nation['nation'][i] in des or Nation['nationality'][i] in des:
            if len(nation)>1:
                nation = des
                break
            nation = Nation['nation'][i]
            continue

    if len(nation) == 1:
        return des,num_educ
    return nation,num_educ



def authors(df):
    authorlist = df['paperResult']['authors']
    FirstAuthor = df['paperResult']['authors'][0]
    l = len(df['paperResult']['authors'])
    educs = [0] * l
    country = ['NA'] * l

    for i in range(l):
        if ifna('displayName',authorlist[i]['currentInstitution']):
            continue
        else:
            if ifna('id',authorlist[i]['currentInstitution']):
                continue
            else:
                time.sleep(1)
                id = authorlist[i]['currentInstitution']['id']
                country[i],educs[i] = CountrySearch(id)

    #print(country)
    num_educ = sum(educs)

    if ifna('displayName',FirstAuthor):
        FirstA = 'NA'
    else:
        FirstA = FirstAuthor['displayName']

    if ifna('currentInstitution',FirstAuthor):
        FirstIns = 'NA'
    else:
        if ifna('displayName',FirstAuthor['currentInstitution']):
            FirstIns='NA'
            FirstNation, FirstEduc = 'NA',0
        else:
            FirstIns = FirstAuthor['currentInstitution']['displayName']
            insID = FirstAuthor['currentInstitution']['id']
            try:
                FirstNation,FirstEduc = CountrySearch(insID)
            except:
                FirstNation, FirstEduc = 'NA', 0

    N = {}
    for j in country:
        if j == 'NA':
            continue
        else:
            N[j] = country.count(j)
    Nations = pd.DataFrame([list(N.values())], columns=list(N.keys()))
    info = pd.DataFrame({'FirstAuthor':[FirstA],
                         'FirstIns':[FirstIns],
                         'IsFirstEduc':[FirstEduc],
                         'num_edu':[num_educ],
                         'num_authors':[l]})
    return info,Nations





def getinfo(content):
    numByear = pd.DataFrame({'T': [10000000]})
    Nations = pd.DataFrame({'T': ['aaaaa']})
    Head = pd.DataFrame({'T': ['A']})
    for j in range(10):
        df = pd.DataFrame(content['paperResults'][j])
        time.sleep(1)
        Total,Byear = author1nd(df)
        PubDate = df['paperResult']['venueInfo']['publishedDate'][0:4]
        Author, N = authors(df)
        #Fields = field(df)

        if ifna('citationCnt',df['paperResult']):
            Citation = -1
        else:
            Citation = df['paperResult']['citationCnt']
        if ifna('estimatedCitationCnt', df['paperResult']):
            estCiteCnt = -1
        else:
            estCiteCnt = df['paperResult']['estimatedCitationCnt']
        if ifna('displayName',df['paperResult']):
            Title = None
        else:
            Title = df['paperResult']['displayName']
        Info = pd.DataFrame({'Title':[Title],'Pubdate':[PubDate],'Citation':[Citation],
                             'estCiteCnt':[estCiteCnt]})
        numByear = pd.concat((numByear,Byear),axis=0,ignore_index=True,                                 sort=True)
        Nations = pd.concat((Nations,N),axis=0,ignore_index=True,sort=True)
        Info = pd.concat((Info,Total,Author), axis=1,ignore_index=True, sort=False)
        Head = pd.concat((Head,Info), axis=0,ignore_index=True, sort=False)

    Head.drop('T',inplace=True,axis=1)
    numByear.drop('T', inplace=True,axis=1)
    Nations.drop('T', inplace=True,axis=1)

    return Head,Nations,numByear



url = 'https://academic.microsoft.com/api/search'

head = pd.DataFrame({'kk':['A']})
nation = pd.DataFrame({'cc':['vv']})
numbyear = pd.DataFrame({'pub':[0000]})

count = 1
num = 17
for series in range(10):
    time.sleep(1)
    for i in range(num*series,num*(series+1)):
        time.sleep(1)
        page = i*10
        content = postsearch(url,page)
        Head, Nations, numByear = getinfo(content)
        head = pd.concat((head,Head),axis=0,ignore_index=True,sort=False)
        nation = pd.concat((nation,Nations),axis=0,ignore_index=True,sort=True)
        numbyear = pd.concat((numbyear,numByear),axis=0,ignore_index=True,sort=True)
        print(count)
        count = count+1



head.drop('kk',inplace=True,axis=1)
numbyear.drop('pub',inplace=True,axis=1)
nation.drop('cc',inplace=True,axis=1)

head.to_csv('ICML_head.csv', header=True)
nation.to_csv('ICML_nation.csv', header=True)
numbyear.to_csv('ICML_byear.csv', header=True)
