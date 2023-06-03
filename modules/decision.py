"""
위험 상태 판별 기준

안전(safe) : 선박 식별 X or 식별된 선박이 AIS 신호를 보내고 먼거리에 있는 경우
경계(warring) : 선박 식별 and AIS 신호 없음
위험(danger) : 식별된 선박이 TCPA 6분 이내 접근 or 위험 거리안에 접근

"""
# TCPA 계산 코드
import math
import pandas as pd
import requests
import json
import pymysql
import private.secret as sc
db = pymysql.connect(host=sc.HOST,user=sc.USER,password=sc.PASSWORD,database=sc.DB)

cur = db.cursor()

# 위/경도로 표시된 두 지점 간의 거리를 계산(Haversine 공식 사용)
def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371  # 지구의 반경 (단위: km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# 두 선박의 Lat, Lon, COG, SOG 정보를 사용하여 TCPA를 계산
def calculate_tcpa(lat1, lon1, cog1, sog1, lat2, lon2, cog2, sog2):
    # 두 선박의 거리 계산
    distance = haversine_dist(lat1, lon1, lat2, lon2)
    # COG 값을 라디안 단위로 변환
    cog1_rad = math.radians(cog1)
    cog2_rad = math.radians(cog2)
    
    # 두 선박의 상대 속도 계산
    relative_speed = math.sqrt(sog1**2 + sog2**2 - 2 * sog1 * sog2 * math.cos(cog2_rad - cog1_rad))
    
    # TCPA 계산
    time_to_closest_point = distance / relative_speed

    # 분 단위로 변환 
    tcpa = time_to_closest_point * 60 

    return int(tcpa)

# TCPA
def tcpa(myaisData:dict,aisData:dict)->bool:
    # tcpa 계산
    # args : ship1_lat, ship1_lon, ship1_sog, ship2_lat, ship2_lon ,ship2_sog
    result = calculate_tcpa(myaisData['Latitude'],myaisData['Longitude'],myaisData['COG'],myaisData['SOG'],
                     aisData['Latitude'],aisData['Longitude'],aisData['COG'],aisData['SOG'])
    # 6분 이내
    print(result)
    if result < 6 or result == None:
        return (False,result)
    # 6분 초과
    else:
        return (True,result)

# 거리 측정
def distance(sensorData)->bool:
    # 거리 계산
    result = sensorData
    # 8m 이내
    if result < 8:
        return False
    else:
        return True

myaisData = pd.read_csv('./ais20171001_top5/ais_top4_mmsi440311690.csv',index_col = 0)
# 선박 위험 상태 판별
def decision(ais:dict,location:str,dist:float)->dict:
    status = {'status':'','distance':dist, 'TCPA':0}
    # AIS 확인
    if len(ais) != 0:
        status['status'] = 'safe'
        
        target_data = myaisData.loc[(myaisData['Date'] == ais['Date']) & (myaisData['Time'] == ais['Time'])].iloc[0]
        
        # 현재 선박 상태 업데이트
        query = f"UPDATE moduleprocessing_shipinfo SET sog={target_data['SOG']}, cog={target_data['COG']} where shipname='happy'"
        cur.execute(query)
        db.commit()

        if not target_data.empty:
            myais = {'MMSI':target_data['MMSI'],'Date':target_data['Date'],
                     'Time':target_data['Time'],'Latitude':target_data['Latitude'],
                     'Longitude':target_data['Longitude'],'SOG':target_data['SOG'],
                     'COG':target_data['COG'],'HDG':target_data['HDG']}
            # TCPA
            tcpav = tcpa(myais,ais)
            status['TCPA'] = tcpav[1]
            if tcpa(myais,ais):
                pass # 안전
            else: # 6분 이내
                status['status'] = 'danger'
            # 위험 거리
            if distance(min(sensorData)): 
                status['status'] = 'warring'
            else: # 가까이옴
                status['status'] = 'danger'

    else :
        status['status'] = 'warring'
        # 위험 거리
        if distance(dist):
            pass
        else: # 가까이옴
            status['status'] = 'danger'

    # 상태값 DB 업데이트
    stage = 0
    if status['status'] == 'safe':
        query = f"UPDATE moduleprocessing_shipinfo SET stage={stage},ais=1,ssas=0,speaker=0,eb=0 where shipname='happy'"
        cur.execute(query)
    elif status['status'] == 'warring': 
        stage = 1
        query = f"UPDATE moduleprocessing_shipinfo SET stage={stage},ais=0,ssas=0,speaker=0,eb=0 where shipname='happy'"
        cur.execute(query)
    elif status['status'] == 'danger': 
        stage = 2
        query = f"UPDATE moduleprocessing_shipinfo SET stage={stage},ais=0,ssas=1,speaker=1,eb=1 where shipname='happy'"
        cur.execute(query)
    db.commit()
    # 페이지 리다이렉트는 현재 미구현... 라이브러리가 동작을 하지 않음
    url = 'http://localhost:5050/control'
    requests.post(url,json=json.dumps(status))
    return status
