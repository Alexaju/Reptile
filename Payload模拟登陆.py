import requests
import json

def login(url,username='xxxxx',password='*****'):
    payloadData = {
        'id':username,
        'password':password
    }
    payloadHeader = {
        'Host': 'openreview.net',
        'Content-Type': 'application/json',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    
     res = ''
    while res=='':
        try:
          res =requests.post(url,json=payloadData,headers=payloadHeader,verify=False)
        except:
          print('sleep for 5 sec before retry')
            time.sleep(5)
            continue

    return res.content




