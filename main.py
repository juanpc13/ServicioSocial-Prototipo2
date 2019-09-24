import time
import ubinascii
from machine import Pin, ADC
import lib.Micropg.micropg as micropg

#Variables del Sistema
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
conn = micropg.connect(host='35.235.111.68', user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)

#Variables de pines
licorPins = [ADC(Pin(35)), ADC(Pin(32))]
acelerometroPins = [ADC(Pin(36)), ADC(Pin(39)), ADC(Pin(34))]

#Modificando el Rango Maximo de 3.3V
#Licor Pins
i = 0
for p in licorPins:
	p.atten(ADC.ATTN_11DB)
	print("licorPin",i,"=",p.read())
	i += 1
#Acelerometro Pins
i = 0
for p in acelerometroPins:
	p.atten(ADC.ATTN_11DB)
	print("acelerometroPin",i,"=",p.read())
	i += 1

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
	#Datos CO2 y rH
		
	#Envio de los datos
	if conn.is_connect():
		cur = conn.cursor()
		cur.execute('select * from acelerometro')
		print("Data is : ")
		for r in cur.fetchall():
   			print(r[0], r[1], r[2], r[3], r[4])
	else:
		print("No Conectado")

	#Delay de 1 segundo
	time.sleep(1)

print("Cerrando Conexion")
conn.close()