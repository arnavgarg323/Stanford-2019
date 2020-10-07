import serial
ser=serial.Serial('/dev/ttyACM2',9600)
ser.write('g')
