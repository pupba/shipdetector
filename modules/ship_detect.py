import torch
import numpy as np
import pandas as pd
import cv2

class ShipDetector:
    def __init__(self) -> None:
        # M1의 경우
        # if torch.backends.mps.is_built() and torch.backends.mps.is_available():
        #     self.__device = torch.device("mps")
        # else: # CPU 사용
        #     print("No GPU")
        self.__device = torch.device("cpu")
        # yolov5 모델 로드
        self.__model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True,device=self.__device)
        # 초당 보여질 이미지
        self.__img = ''

        # 감지한 선박 리스트
        self.__shipList = {}

        # 배
        self.__ship = 8

    # 선박 식별 후 바운딩 박스 함수 호출하는 메서드
    def detect(self,cap:np.ndarray)->None:
        self.__img = cap
        results = self.__model(self.__img)
        self.makeBBox(results)

    # 식별된 선박을 트래킹하면서 바운딩 박스 그리는 메서드
    def makeBBox(self,results:pd.DataFrame)->None:
        obj_idx = None
        color = (0,0,0)
        for resultDF in results.pandas().xyxy:
            # 배가 사라지면 사라진 객체 삭제
            self.__shipList = {}
            for result in resultDF.iterrows():
                # 위험 상태 판별
                status = {'status':'warring'}
                
                # 상태 값에 따라 바운딩 박스의 색을 다르게
                if status['status'] == 'safe':
                    color = (0,255,0) # 안전
                elif status['status'] == 'warring':
                    color = (0,255,255) # 주의
                elif status['status'] == 'danger':
                    color = (0,0,255) # 위험        

                # 추적할 객체가 배일 경우
                # 0은 사람, 배 번호로 나중에 변경
                # boat 8번
                if result[1][5] == self.__ship:
                    # 객체의 인덱스를 저장
                    obj_idx = int(result[0])
                    # 추적할 bounding box를 저장
                    obj_box = np.array(result[1][0:4])
                    if obj_idx not in self.__shipList:
                        self.__shipList[obj_idx] = obj_box
                    else:
                        # 이전 위치와 새로운 위치를 비교하여 거리가 가장 가까운 위치를 선택
                        dist = np.linalg.norm(self.__shipList[obj_idx] - obj_box)
                        if dist < 50:
                            self.__shipList[obj_idx] = obj_box
                    # bounding box 그리기
                    cv2.rectangle(self.__img, (int(obj_box[0]), int(obj_box[1])), (int(obj_box[2]), int(obj_box[3])), color, 2)
                    cv2.putText(self.__img, f'Person{obj_idx}', (int(obj_box[0]), int(obj_box[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
                else: # 배가 아닐 경우
                    pass