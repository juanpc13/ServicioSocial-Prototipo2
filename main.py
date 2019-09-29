from machine import Timer
import time
import machine
import ubinascii
from machine import Pin, ADC
import lib.Micropg.micropg as micropg

#Variables del Sistema
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
conn = micropg.connect(host='35.235.111.68', port=1000,user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)
#Variables del timmer para mejor presicion del tiempo
tim = Timer(-1)

#Licor Variable
licorCounter = 0 # Contador de la licor en segundos
licorStop = 60*12 # Apagar en el minuto 12 y expresarlo en segundos
licorCollectData = 60*2 # Recolectar datos desde el minuto 2 y expresarlo en segundos
licorDelay = 60*60 # 60 Minutos totales para cada dato y expresarlo en segundos
licorPower = Pin(13, Pin.OUT)
licorPins = [ADC(Pin(35)), ADC(Pin(32))]
#Acelerometro Variable
acelerometroPins = [ADC(Pin(36)), ADC(Pin(39)), ADC(Pin(34))]

#Modificando el Rango Maximo de 3.3V
#Licor Pins
for p in licorPins:
	p.atten(ADC.ATTN_11DB)	
#Acelerometro Pins
for p in acelerometroPins:
	p.atten(ADC.ATTN_11DB)

#Ecuacion para Acelerometro
def acelerometroConversion(x):
	x1 = 1400.0
	y1 = -9.8
	x2 = 2175.0
	y2 = 9.8
	y = 0.0
	y = ((y2-y1)/(x2-x1))*(x-x1)+y1
	return y

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

def sendQuery(conn, query):
	try:
		cur = conn.cursor()		
		cur.execute(query)
		conn.commit()
		print("SEND:",query)
	except:
		machine.reset()

#Dispositivo
id_dispositivo = None
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
	print("Registrando Dispositivo")
	cur = conn.cursor()
	cur.execute("INSERT INTO dispositivo(nombre, mac, activo) VALUES('Prototipo2', '"+mac+"', true)")
	conn.commit()
	cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
	id = cur.fetchone()
	if id is not None:
		id = id[0]
		print("idDispositivo: ", id)
	return id		

def prototipo2():	
	#Recolectar los datos y enviarlos
	global conn
	global licorCounter
	global id_dispositivo
	if id_dispositivo is not None:
		#Recoleccion de los datos	
		query = "" #Vaciar Query
		query += "SET TIMEZONE='America/El_Salvador';"
		#Datos Acelerometro
		query += "INSERT INTO acelerometro(id_dispositivo, x, y, z) VALUES(?,?,?,?);"
		query = query.replace('?',str(id_dispositivo), 1)
		for p in acelerometroPins:
			aceleracion = acelerometroConversion(p.read())
			query = query.replace('?',str(aceleracion), 1)
		# Verificar si es necesario en Encender la licor		
		if licorCounter <= licorStop:
			licorPower.on()
			# Esperar a que caliente la licor
			if licorCounter >= licorCollectData:
				#Datos CO2
				query += "INSERT INTO co2(id_dispositivo, ppm) VALUES(?,?);"
				query = query.replace('?',str(id_dispositivo), 1)
				value = licorPins[0].read()
				value = map(value, 745, 3722, 0, 20000)
				value = constrain(value, 0, 20000)
				query = query.replace('?',str(value), 1)

				#Datos rH
				query += "INSERT INTO h2o(id_dispositivo, rh) VALUES(?,?);"
				query = query.replace('?',str(id_dispositivo), 1)
				value = licorPins[1].read()
				value = map(value, 745, 3722, 0, 60)
				value = constrain(value, 0, 60)
				query = query.replace('?',str(value), 1)
		else:
			licorPower.off()

		#Envio de los datos		
		sendQuery(conn, query)
		#Aumentar el Contador de la licor y verificar reinicio 
		licorCounter += 1
		if licorCounter > licorDelay:
			licorCounter = 0
			print("Reiniciando licorCounter")

	else:
		print("idDispositivo No Definido")
		if conn is None:
			time.sleep(5)
			machine.reset()
		elif id_dispositivo is None:
			#Buscar ID del dispositivo
			id_dispositivo = findDevice(mac)			
			if id_dispositivo is None:
				#Registrar el Dispositivo
				id_dispositivo = registerDevice(mac)
				if id_dispositivo is None:
					print("No se puede registrar")


tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:prototipo2())