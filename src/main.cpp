#include <Arduino.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>

//Inicializar los servicio
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

//Datos de la Conexion
const char *ssid = "TURBONETT_1DFD27";
const char *password = "57E04D255E";

//Variables Principales
int dataDelay = 1000;//En millisegundos el dato del WebSocket
double delayFactor = 0.1;//El porcentaje de dataDelay para promediar dato final
int delayCounter = 0;//ciclos de la iteracion de cada factor de lectura
//Pins y Datos del Acelerometro
uint8_t acelerometroPins[] = {36, 39, 34};
double aceletrometroData[sizeof(acelerometroPins) / sizeof(acelerometroPins[0])];
//Pins y Datos de la licor
uint8_t licorPins[] = {35, 32};
double licorData[sizeof(licorPins) / sizeof(licorPins[0])];

//Datos de la RED
IPAddress local_IP(192, 168, 1, 251);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);

//Eventos del WebSocket
void onWsEvent(AsyncWebSocket * server, AsyncWebSocketClient * client, AwsEventType type, void * arg, uint8_t *data, size_t len){

  if(type == WS_EVT_CONNECT){
    Serial.println("Client connected");
  } else if(type == WS_EVT_DISCONNECT){
    Serial.println("Client disconnected");
  } else if(type == WS_EVT_DATA){
    Serial.println("Client Recive Data");    
  }

}

double acelerometroEcuacion(double x){
  double x1 = 1400.0, y1 = -9.8;
  double x2 = 2175.0, y2 = 9.8;
  double y = 0.0;
  y = ((y2-y1)/(x2-x1))*(x-x1)+y1;
  return y;
}

void setup() {
  //Puerto Serial
  Serial.begin(115200);
  Serial.println();
  //Memoria SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    while (1);
  }
  //Conectar Wifi
  //WiFi.softAP("ESP32", "87654321");
  // Configures static IP address
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");delay(100);
  }  
  //Mostrar IP
  Serial.print("IP : ");Serial.println(WiFi.localIP());
  //Server Config
  server.serveStatic("/", SPIFFS, "/").setDefaultFile("index.html");
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);
  server.begin();
}

void loop() {
  //Recolectar los Datos
  uint8_t s = 0;

  //Recolectando datos del acelerometro
  s = sizeof(acelerometroPins) / sizeof(acelerometroPins[0]);
  for(uint8_t i = 0; i < s; i++){
    aceletrometroData[i] += analogRead(acelerometroPins[i]);
  }
  //Recolectando datos de la licor
  s = sizeof(licorPins) / sizeof(licorPins[0]);
  for(uint8_t i = 0; i < s; i++){    
    licorData[i] += analogRead(licorPins[i]);    
  }

  //Aumentar el contador delayCounter para ver si ya es necesario Enviar los datos en relacion al dataDelay y el delayFactor 
  //Generar un retardo por dato de 10% de dataDelay con delayFactor (1000 / 10) = 100ms
  delayCounter ++;
  delay(dataDelay*delayFactor);
  

  //Enviar la respuesta por el WebSocket despues del dataDelay
  if(delayCounter*dataDelay*delayFactor >= dataDelay){
    //Variables para almacenar los datos y Responder al WebSocket
    String text = "";
    StaticJsonDocument<256> doc;
    JsonObject root = doc.to<JsonObject>();

    //Recolectando datos del acelerometro
    s = sizeof(acelerometroPins) / sizeof(acelerometroPins[0]);
    for(uint8_t i = 0; i < s; i++){
      //Calcular el promedio de lo recolectado del dataDelay con el delayFactor
      aceletrometroData[i] = (aceletrometroData[i] / delayCounter);
      aceletrometroData[i] = acelerometroEcuacion(aceletrometroData[i]);
      //Enviar y Vaciar el dato
      root["aceletrometro"+String(i)] = String(aceletrometroData[i], 4);
      aceletrometroData[i] = 0.0;
    }
    //Recolectando datos de la licor
    s = sizeof(licorPins) / sizeof(licorPins[0]);
    for(uint8_t i = 0; i < s; i++){
      //Calcular el promedio de lo recolectado del dataDelay con el delayFactor
      licorData[i] = (licorData[i] / delayCounter);

      //Enviar y Vaciar el dato
      root["licor"+String(i)] = String(licorData[i], 4);
      licorData[i] = 0.0;
    }
    serializeJson(doc, text);
    ws.textAll(text.c_str());
    //Resetear el counter para poder Enviar otra vez la respuesta
    delayCounter = 0;
  }  
}