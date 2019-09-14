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
uint8_t acelerometroPins[] = {36, 39, 34};
uint8_t licorPins[] = {35, 32};
double aceletrometroData[sizeof(acelerometroPins) / sizeof(acelerometroPins[0])];
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

  //Variables para almacenar los datos y Responder al WebSocket
  String text = "";
  StaticJsonDocument<256> doc;
  JsonObject root = doc.to<JsonObject>();
  uint8_t s = 0;

  //Recolectando datos del acelerometro
  s = sizeof(acelerometroPins) / sizeof(acelerometroPins[0]);
  for(uint8_t i = 0; i < s; i++){
    aceletrometroData[i] = 0.0;
    for(uint8_t r = 0; r < 8; r++){
      aceletrometroData[i] += analogRead(acelerometroPins[i]);
    }
    aceletrometroData[i] = (aceletrometroData[i] / 8.0);
    root["aceletrometro"+String(i)] = (double) aceletrometroData[i];
  }
  //Recolectando datos de la licor
  s = sizeof(licorPins) / sizeof(licorPins[0]);
  for(uint8_t i = 0; i < s; i++){
    licorData[i] = 0.0;
    for(uint8_t r = 0; r < 8; r++){
      licorData[i] += analogRead(licorPins[i]);
    }
    licorData[i] = (licorData[i] / 8.0);
    root["licor"+String(i)] = (double) licorData[i];
  }

  //Enviar la respuesta por el WebSocket
  serializeJson(doc, text);
  ws.textAll(text.c_str());
  delay(1000);
}