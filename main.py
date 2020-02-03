from machine import Timer
import time
import ujson
import machine
import ubinascii
from machine import Pin, I2C
import lib.Micropg.micropg as micropg
import lib.ADS.ads1x15 as ads1x15

#Variables del Sistema
led = Pin(2, Pin.OUT)
led.off()
id_dispositivo = None
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
adsAdd = 0x48
ads = None
#Verificar que existe el ADS
if adsAdd in i2c.scan():
	print("Direccion 0x48 Encontrada")
	ads = ads1x15.ADS1115(i2c, address=0x48, gain=2)
	print("Modulo Declarado")
#Cargar datos de calibracion
f = open("calibration.json")
calibration = ujson.loads(f.read())
f.close()

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
conn = micropg.connect(host='34.70.49.21', port=1000,user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)
#Variables del timmer para mejor presicion del tiempo
tim = Timer(-1)

def adsRead(pin):
	# Samples per second
	# 4 _DR_1600SPS,  1600/128
	# 5 _DR_2400SPS,  2400/250
	try:
		return ads.read(rate=5, channel1=pin)
	except:
		rebootDelayMessage(2, "Fallo al leer Modulo ADS...Reiniciando")
		return 0.0

def map(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def constrain(value, min, max):
	if value <= min:
		value = min
	elif value >= max:
		value = max
	return value

def rebootDelayMessage(delaySeconds, message):
	print(message)
	led.off()
	time.sleep(delaySeconds)
	machine.reset()

def sendQuery(conn, query):
	try:
		led.on()
		cur = conn.cursor()		
		cur.execute(query)
		conn.commit()
		print("SEND:",query)
		led.off()
	except:
		rebootDelayMessage(2, "Fallo al enviar QUERY...Reiniciando")

#Buscar
def findDevice(mac):
	id = None
	cur = conn.cursor()
	cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
	id = cur.fetchone()
	if id is not None:
		id = id[0]
		print("idDispositivo: ",id)
	return id

#Registrar
def registerDevice(mac):
	id = None
	cur = conn.cursor()
	cur.execute("INSERT INTO dispositivo(nombre, mac, activo) VALUES('Prototipo2', '"+mac+"', true)")
	conn.commit()
	cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
	id = cur.fetchone()
	if id is not None:
		id = id[0]
	return id

def loopRaw():
	while True:
		x = adsRead(0)
		y = adsRead(1)
		z = adsRead(2)
		ppm = adsRead(3)
		print(x, ' ', y, ' ', z, ' ', ppm)

def prototipo2():
	#Recolectar los datos y enviarlos
	global conn
	global id_dispositivo
	if id_dispositivo is not None and ads is not None:
		#Recoleccion de los datos	
		query = "" #Vaciar Query
		query += "SET TIMEZONE='America/El_Salvador';"
		#Datos Acelerometro
		query += "INSERT INTO acelerometro(id_dispositivo,x,y,z) VALUES(?,?,?,?);"
		query = query.replace('?',str(id_dispositivo), 1)
		
		#Iterador de los 3 EJES(X, Y y Z)
		i = 0
		while i < 3:
			i += 1
		#Obtener Datos de X corresponde a A0 del ADS en posicion 0
		aceleracion = 0.0
		aceleracion = map((adsRead(0)), calibration["xVOL1"], calibration["xVOL2"], calibration["xACE1"], calibration["xACE2"])
		query = query.replace('?', '{:.8f}'.format(aceleracion), 1)

		#Obtener Datos de Y corresponde a A1 del ADS en posicion 1
		aceleracion = 0.0
		aceleracion = map((adsRead(1)), calibration["yVOL1"], calibration["yVOL2"], calibration["yACE1"], calibration["yACE2"])
		query = query.replace('?', '{:.8f}'.format(aceleracion), 1)

		#Obtener Datos de Z corresponde a A2 del ADS en posicion 2
		aceleracion = 0.0
		aceleracion = map((adsRead(2)), calibration["zVOL1"], calibration["zVOL2"], calibration["zACE1"], calibration["zACE2"])
		query = query.replace('?', '{:.8f}'.format(aceleracion), 1)

		#Datos CO2 Corresponde al pin A3 del ADS en posicion 3
		ppm = 0.0
		query += "INSERT INTO co2(id_dispositivo, ppm) VALUES(?,?);"
		query = query.replace('?',str(id_dispositivo), 1)
		ppm = map((adsRead(3)), calibration["dragerVOL1"], calibration["dragerVOL2"], calibration["dragerPPM1"], calibration["dragerPPM2"])
		query = query.replace('?', '{:.8f}'.format(ppm), 1)

		
		#Envio de los datos
		sendQuery(conn, query)
		
	elif id_dispositivo is None:
		print("idDispositivo No Definido")
		#Buscar ID del dispositivo
		id_dispositivo = findDevice(mac)
		if id_dispositivo is None:
			#Registrar el Dispositivo
			print("Registrando Dispositivo")
			id_dispositivo = registerDevice(mac)
			if id_dispositivo is not None:
				print("idDispositivo: ", id_dispositivo)
			else:
				rebootDelayMessage(2, "No se puedo registrar dispositivo...Reiniciando")

	elif ads is None:
		rebootDelayMessage(2, "Modulo ADS no ha sido encontrado...Reiniciando")

tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:prototipo2())