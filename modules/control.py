"""
자동 제어 코드
safe : AIS ON
warring : AIS OFF 
danger : AIS OFF and ALL ON
"""
import MySQLdb
import private.secret as sc
db = MySQLdb.connect(host=sc.HOST,user=sc.USER,password=sc.PASSWORD,database=sc.DB)

cur = db.cursor()
def controler(status):
    if status == 'safe': # 0단계 동작 코드
        print(status)
    elif status == 'warring': # 1단계 동작 코드
        print(status)
    elif status == 'danger': # 2단계 동작 코드
        print(status)
    elif status == -1: # 수동 제어
        query = f"select ais,ssas,speaker,eb from moduleprocessing_shipinfo where shipname='happy'"
        cur.execute(query)
        results = cur.fetchall()
        for row in results:
            # 0 : ais
            if row[0] == 1: # 동작
                pass
            else: # 멈춤
                pass
            # 1 : ssas
            if row[1] == 1: # 동작
                pass
            else: # 멈춤
                pass
            # 2 : speaker
            if row[2] == 1: # 동작
                pass
            else: # 멈춤
                pass
            # 3 : eb
            if row[3] == 1: # 동작
                pass
            else: # 멈춤
                pass
        print(end='\n\n')