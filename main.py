import time
import ubinascii
import lib.Micropg.micropg as micropg

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
conn = micropg.connect(host='35.235.111.68', user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)

#Check this Device
id_dispositivo = None
if conn.is_connect():
	#Find
	cur = conn.cursor()
	cur.execute("SELECT d.id_dispositivo FROM dispositivo as d WHERE d.mac='"+mac+"'")
	id_dispositivo = cur.fetchone()
	if id_dispositivo is not None:
		id_dispositivo = id_dispositivo[0]
		print(id_dispositivo)
else:
	print("No Conected")


while conn.is_connect() and id_dispositivo is not None:

	if conn.is_connect():
		cur = conn.cursor()
		cur.execute('select * from acelerometro')
		for r in cur.fetchall():
   			print("Data is : ",r[0], r[1], r[2], r[3], r[4])
	else:
		print("No Conected")
		
	#Delay de 1 segundo
	time.sleep(1)

print("Cerrando Conexion")
conn.close()