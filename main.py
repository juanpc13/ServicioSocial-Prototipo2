import time
import ubinascii
from machine import Pin, ADC
import lib.Micropg.micropg as micropg

#Variables del Sistema
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
conn = micropg.connect(host='192.168.1.251', user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)

#Licor Variable
licorCounter = 0 # Contador de la licor
licorDelay = 60*10 # 10 Minutos
licorStart = 60*8 # Encender en el minuto 8
licorCollectData = 60*9 # Recolectar datos desde el minuto 9
licorPower = Pin(2, Pin.OUT)
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

def sendQuery(conn, query):
	if conn.is_connect():
		cur = conn.cursor()		
		cur.execute(query)
		conn.commit()
		print("SEND:",query)
	else:
		print("No Conectado")


#Verificar este dispositivo
id_dispositivo = None
if conn.is_connect():
	#Buscar
	cur = conn.cursor()
	cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
	id_dispositivo = cur.fetchone()
	if id_dispositivo is not None:
		id_dispositivo = id_dispositivo[0]
		print("idDispositivo: ",id_dispositivo)

	#Registrar
	if id_dispositivo is None:
		print("Dispositivo no encontrado, Se registrara")
		cur = conn.cursor()
		cur.execute("INSERT INTO dispositivo(nombre, mac, activo) VALUES('Prototipo2', '"+mac+"', true)")
		conn.commit()
		cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
		id_dispositivo = cur.fetchone()
		if id_dispositivo is not None:
			id_dispositivo = id_dispositivo[0]
			print("idDispositivo: ", id_dispositivo)
		else:
			print("Error no se puede Registar... Reiniciando")			
			time.sleep(3)
			machine.reset()
else:
	print("No Conectado... Reiniciando")	
	time.sleep(3)
	machine.reset()

#Recolectar los datos y enviarlos
while id_dispositivo is not None:

	#Recoleccion de los datos
	#Datos Acelerometro
	query = "INSERT INTO acelerometro(id_dispositivo, x, y, z) VALUES(?,?,?,?)"
	query = query.replace('?',str(id_dispositivo), 1)
	for p in acelerometroPins:
		aceleracion = acelerometroConversion(p.read())
		query = query.replace('?',str(aceleracion), 1)
	#Envio de los datos
	sendQuery(conn, query)

	# Verificar si es necesario en Encender la licor
	if licorCounter >= licorStart:
		licorPower.on()
		# Esperar a que caliente la licor
		if licorCounter >= licorCollectData:
			#Datos CO2
			query = "INSERT INTO co2(id_dispositivo, ppm) VALUES(?,?)"
			query = query.replace('?',str(id_dispositivo), 1)
			value = licorPins[0].read()
			query = query.replace('?',str(value), 1)
			#Envio de los datos
			sendQuery(conn, query)

			#Datos rH
			query = "INSERT INTO h2o(id_dispositivo, rh) VALUES(?,?)"
			query = query.replace('?',str(id_dispositivo), 1)
			value = licorPins[1].read()
			query = query.replace('?',str(value), 1)
			#Envio de los datos
			sendQuery(conn, query)			
	else:
		licorPower.off()
	

	#Delay de 1 segundo
	time.sleep(1)
	#Aumentar el Contador de la licor y verificar reinicio 
	licorCounter += 1
	if licorCounter > licorDelay:
		licorCounter = 0
		print("Reiniciando licorCounter")

print("Cerrando Conexion")
conn.close()