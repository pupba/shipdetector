import ydlidar
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import requests
import json
from io import BytesIO
import time

class Lidar:
    def __init__(self):
        self.__RMAX = 32.0
        self.__fig = plt.figure(facecolor='#6495ED')
        self.__lidar_polar = self.__fig.add_subplot(111,polar=True)
        self.__lidar_polar.autoscale_view(True,True,True)
        self.__lidar_polar.set_rmax(self.__RMAX)
        self.__lidar_polar.grid(True)


        self.__lidar_polar.spines['polar'].set_color('black')
        self.__lidar_polar.spines['polar'].set_linewidth(2)
        self.__lidar_polar.fill_between([0,2*np.pi],0,self.__RMAX,facecolor='green',edgecolor='green')

        self.__laser = ydlidar.CYdLidar()
        self.__scan = ydlidar.LaserScan()
        
        self.rd = []
        self.ld = []

    def __animate(self,num): 
        r = self.__laser.doProcessSimple(self.__scan);
        if r:
            angle = []
            ran = []
            intensity = []
            for point in self.__scan.points: 
                angle.append(point.angle);
                ran.append(point.range);
                intensity.append(point.intensity);
                
                x= point.range * np.cos(np.radians(point.angle))
                y= point.range * np.sin(np.radians(point.angle))
                self.__lidar_polar.text(point.angle, point.range, f"{point.range:.2f}",fontsize=5,ha='center',va='center',color='white')
            self.__lidar_polar.clear()
            self.__lidar_polar.scatter(angle, ran, c='#FF0000', cmap='hsv', alpha=0.95)


    def run_lidar(self):
        ret = self.__laser.initialize()
        if ret:
            ret = self.__laser.turnOn()
            if ret:
                #plt.show()
                
                try:
                    while True:
                        ani = animation.FuncAnimation(self.__fig, self.__animate, frames=None,interval=50,cache_frame_data=False)
                        r = self.__laser.doProcessSimple(self.__scan)
                        if r:
                            time.sleep(0.1)
                            object_distances_1 = {}
                            object_distances_2 = {}
                            
                            for point in self.__scan.points:
                                x= point.range * np.cos(np.radians(point.angle))
                                y= point.range * np.sin(np.radians(point.angle))
                                distance = point.range
                            
                                if point.angle >= 0 and point.angle < 180:
                                    object_distances_1[(int(x),int(y))] = distance
                                    if distance != 0.0:
                                        self.ld.append(distance)
                                else:
                                    object_distances_2[(int(x),int(y))] = distance
                                    if distance != 0.0:
                                        self.rd.append(distance)
                                        
                            buffer = BytesIO()
                            plt.savefig(buffer, format='png')
                            buffer.seek(0)
                            frame_bytes = buffer.getvalue()
                        
                            time.sleep(1)
                            data = {'l':self.ld,'r':self.rd}
                            url = 'http://localhost:5050/locate'
                            resp = requests.post(url,json=json.dumps(data))
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/png\r\n\r\n' + frame_bytes + b'\r\n')
                except KeyboardInterrupt:
                    laser.turnOff()
                    laser.disconnecting()

if __name__=="__main__":
    ld = Lidar()
    ld.run_lidar()
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    