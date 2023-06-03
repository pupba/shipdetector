from flask import Flask
import requests, time
import pandas as pd
import threading
import itertools
import json

aissender = Flask(__name__)
# 주선박 top3
# 타선박1(경계) : top4
# 타선박2(위험) : top5
AISDATA = pd.read_csv('./ais20171001_top5/ais_top3_mmsi440123380.csv',index_col = 0)
#AISDATA = pd.read_csv('./ais20171001_top5/ais_top5_mmsi440032230.csv',index_col = 0)

def send(data:pd.DataFrame)->bool:
    url = 'http://localhost:5050/recv'
    resp = requests.post(url,json=json.dumps(data.to_dict()))

    if resp.status_code == 200:
        return True
    else:
        return False
def bicon():
    l = list(AISDATA.index)
    n = itertools.cycle(range(len(l))) 
    while True:   
        if send(AISDATA.loc[l[next(n)]]):
            time.sleep(5)
        else:
            print("Error")
            break
if __name__ == '__main__':
    sendThread = threading.Thread(target=bicon)
    sendThread.start()

    aissender.run(debug=False, host='0.0.0.0',port=8081)
