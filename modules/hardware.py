import RPi.GPIO as GPIO

class Hardware:
    def __init__(self):
        self.__IN1 = 17
        self.__IN2 = 18
        self.__LED_PIN = 27

        self.__BUZZER_PIN = 23

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.__IN1,GPIO.OUT)
        GPIO.setup(self.__IN2,GPIO.OUT)
        GPIO.setup(self.__LED_PIN,GPIO.OUT)
        GPIO.setup(self.__BUZZER_PIN,GPIO.OUT)
    
    # speaker
    def speaker_contorl(self,msg:str):
        if msg == 'on':
            GPIO.output(self.__BUZZER_PIN, GPIO.HIGH) # speaker
        elif msg == 'off' :
            GPIO.output(self.__BUZZER_PIN, GPIO.LOW) # Speaker

            
    # Electronic Blow
    def EB_control(self,msg:str):
        if msg == 'on':
            GPIO.output(self.__IN1,GPIO.HIGH) # water
            GPIO.output(self.__LED_PIN,GPIO.HIGH) # LED
        elif msg == 'off' :
            GPIO.output(self.__IN1,GPIO.LOW) # water
            GPIO.output(self.__LED_PIN,GPIO.LOW) # LED
            
if __name__ == '__main__':
    hd = Hardware()
    hd.speaker_contorl('off')
    hd.EB_control('off')
