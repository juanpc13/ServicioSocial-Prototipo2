import lib.Micropg.micropg as micropg
from lib.MicroWebSrv.microWebSrv import MicroWebSrv

# ------------------WebSocket------------------------------------
def _acceptWebSocketCallback(webSocket, httpClient) :
	print("WS ACCEPT")
	webSocket.RecvTextCallback   = _recvTextCallback
	webSocket.RecvBinaryCallback = _recvBinaryCallback
	webSocket.ClosedCallback 	 = _closedCallback

def _recvTextCallback(webSocket, msg) :
	print("WS RECV TEXT : %s" % msg)
	webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
	print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
	print("WS CLOSED")
# -----------------------------------------------------------------



mws = MicroWebSrv(webPath="/webapp")                    # TCP port 80 and files in /flash/www
mws.MaxWebSocketRecvLen     = 256                       # Default is set to 1024
mws.WebSocketThreaded       = False                     # WebSockets without new threads
mws.AcceptWebSocketCallback = _acceptWebSocketCallback  # Function to receive WebSockets
mws.Start(threaded=True)                                # Starts server in a new thread

'''conn = micropg.connect(host='35.235.111.68', user='postgres', password='Cal15!', database='prototipo2', use_ssl=False)

cur = conn.cursor()
cur.execute('select * from acelerometro')
for r in cur.fetchall():
   print(r[0], r[1], r[2], r[3])


conn.close()
'''