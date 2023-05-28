
import math

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

    return tcpa

# top3, top4, top5 선박 데이터 읽기
import pandas as pd
mmsi3_ais = pd.read_csv('./ais20171001_top5/ais_top3_mmsi440123380.csv')
mmsi4_ais = pd.read_csv('./ais20171001_top5/ais_top4_mmsi440311690.csv')
mmsi5_ais = pd.read_csv('./ais20171001_top5/ais_top5_mmsi440032230.csv')


# mmsi4 시작 한 지점에서 mmsi3 데이터에 대한 TCPA 계산 
# mmsi3 데이터를 TCPA 6분 이내(near)와 이상(far)으로 나눠 시각화 

main_ais = mmsi4_ais.iloc[0]
mmsi3_near = pd.DataFrame(columns = mmsi3_ais.columns )
mmsi3_far = pd.DataFrame(columns = mmsi3_ais.columns )

for i in range(len(mmsi3_ais)) :
  target =  mmsi3_ais.iloc[i] 
  tcpa_m = calculate_tcpa(main_ais.Latitude, main_ais.Longitude, main_ais.COG, main_ais.SOG, 
                   target.Latitude, target.Longitude, target.COG, target.SOG)
  if tcpa_m < 6 :
    mmsi3_near = pd.concat([mmsi3_near, mmsi3_ais.iloc[i:i+1]]) 
  else :
    mmsi3_far = pd.concat([mmsi3_far, mmsi3_ais.iloc[i:i+1]])

import matplotlib.pyplot as plt
import numpy as np
plt.scatter(main_ais.Longitude, main_ais.Latitude, s=3, marker= '*', color='blue', label='main-ship4')
plt.scatter(mmsi3_near.Longitude, mmsi3_near.Latitude, s=3 , c='red', label='target-ship3 : danger')
plt.scatter(mmsi3_far.Longitude, mmsi3_far.Latitude, s=3, marker='^', c='green', label='target-ship3 : safe')
plt.xlabel('Lon.')
plt.ylabel('Lat.')
plt.xticks(np.arange(126.325, 126.345, 0.004))
plt.yticks(np.arange(34.760, 34.785, 0.005)) 
plt.legend()
plt.show()


# mmsi4 시작 한 지점에서 mmsi5 데이터에 대한 TCPA 계산 
# mmsi5 데이터를 TCPA 6분 이내(near)와 이상(far)으로 나눠 시각화 

main_ais = mmsi4_ais.iloc[0]
mmsi5_near = pd.DataFrame(columns = mmsi5_ais.columns )
mmsi5_far = pd.DataFrame(columns = mmsi5_ais.columns )

for i in range(len(mmsi5_ais)) :
  target =  mmsi5_ais.iloc[i] 
  tcpa_m = calculate_tcpa(main_ais.Latitude, main_ais.Longitude, main_ais.COG, main_ais.SOG, 
                   target.Latitude, target.Longitude, target.COG, target.SOG)
  if tcpa_m < 6 :
    mmsi5_near = pd.concat([mmsi5_near, mmsi5_ais.iloc[i:i+1]]) # ignore_index = True)
  else :
    mmsi5_far = pd.concat([mmsi5_far, mmsi5_ais.iloc[i:i+1]])
  
import matplotlib.pyplot as plt
import numpy as np
plt.scatter(main_ais.Longitude, main_ais.Latitude, s=3, marker= '*', color='blue', label='main-ship4')
plt.scatter(mmsi5_near.Longitude, mmsi5_near.Latitude, s=3 , c='red', label='target-ship5 : danger')
plt.scatter(mmsi5_far.Longitude, mmsi5_far.Latitude, s=3, marker='^', c='purple', label='target-ship5 : safe')
plt.xlabel('Lon.')
plt.ylabel('Lat.')
plt.xticks(np.arange(126.325, 126.345, 0.004))
plt.yticks(np.arange(34.760, 34.785, 0.005)) 
plt.legend()
plt.show()