#!usr/bin/python

from RPi import GPIO
import string, time, subprocess, os

DELAY = 0.45
RIGHT = 8
LEFT  = 10
LED   = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RIGHT, GPIO.IN)
GPIO.setup(LEFT, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)

#This is added in case several Rpi's are used, so that it's clear which feedback came from which one
def setfilename(asctime):
    FILEROOT = '/home/pi/Mood_Logs/MElog_'
    macline = subprocess.check_output('ifconfig | grep b8:27:eb',shell=True)
    mac = macline[-11:-3]
    temp1 = string.replace(asctime,':','-')
    temp2 = string.replace(temp1,' ','_')
    temp3 = string.replace(mac, ':','_')
    FILENAME = FILEROOT + temp3 + '_' + temp2 + '.txt' 
    return (FILENAME, temp3)

# Blink a few times to know that the program is running
for n in range(4):
    GPIO.output(LED,GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(LED,GPIO.LOW)
    time.sleep(0.2)

#Initialize log file and close it
logfilename, mac = setfilename(time.asctime())
logfile = open(logfilename,'w')
logfile.close()

while True:
    input_value_right = GPIO.input(RIGHT)
    input_value_left  = GPIO.input(LEFT)

    if input_value_right and not input_value_left:
        print('Right', time.asctime())
        logfile = open(logfilename,'a')
        logfile.write(mac + ' Right, ' +  time.asctime() + '\n')
        logfile.close()

        #Blink so that the user knows that input has been recorded
        GPIO.output(LED,GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(LED,GPIO.LOW)

    
    if not input_value_right and input_value_left:
        print('Left', time.asctime())
        logfile = open(logfilename,'a')
        logfile.write(mac + ' Left, ' + time.asctime() + '\n')
        logfile.close()

        #Blink so that the user knows that input has been recorded
        GPIO.output(LED,GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(LED,GPIO.LOW)

    if input_value_right and input_value_left:
        print('both')
        #Blink so I know that upload is launched
        for n in range(4):
            GPIO.output(LED,GPIO.HIGH)
            time.sleep(DELAY/2)
            GPIO.output(LED,GPIO.LOW)
            time.sleep(DELAY/2)

        logfile.close()

        mycommand = '/home/pi/Dropbox-Uploader/dropbox_uploader.sh'
        print(mycommand)
        print(os.getcwd())
        #-s skips files which already exist
        input_list = ['sudo', mycommand, '-s' , 'upload', 'Mood_Logs', '/']
        print(input_list)

        GPIO.output(LED,GPIO.HIGH)
        subprocess.call(['sudo', 'ifdown', 'wlan0'])
        subprocess.call(['sudo', 'ifup', 'wlan0'])
        subprocess.call(input_list)
        GPIO.output(LED, GPIO.LOW)

        #Blink so I know that upload is finished
        for n in range(4):
            GPIO.output(LED,GPIO.HIGH)
            time.sleep(DELAY/2)
            GPIO.output(LED,GPIO.LOW)
            time.sleep(DELAY/2)

        logfilename, mac = setfilename(time.asctime())
        logfile = open(logfilename,'w')
        logfile.close()



