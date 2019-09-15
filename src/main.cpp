#include <Arduino.h>
#include <SPIFFS.h>
#include "RTClib.h"
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
//Reloj
DateTime now;
DateTime lastTime;
RTC_DS1307 rtc;

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
  //RTC
  if (! rtc.begin(33, 25)) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  if (! rtc.isrunning()) {
    Serial.println("RTC is NOT running!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));    
  }
  now = rtc.now();
  //Mostrar IP
  Serial.print("IP : ");Serial.println(WiFi.localIP());
  
  //Crear archivos con 3 dias de diferencia con las fechas  
  StaticJsonDocument<256> doc;
  JsonObject object = doc.to<JsonObject>();
  JsonArray allowFiles = object.createNestedArray("allowFiles");
  uint8_t interval = 3;//3dias
  for (uint8_t i = 0; i < interval; i++)  {
    //Generar el nombre del archivo con la fecha
    String filename = "/dataFiles/" + now.timestamp(DateTime::timestampOpt::TIMESTAMP_DATE) +".txt";
    //Crear o Abrir archivo
    File f = SPIFFS.open(filename, FILE_APPEND);f.close();
    //Agregar a los archivos permitidos a la lista
    allowFiles.add(filename);
    //Quitamos un dia al tiempoUNIX
    now = now.unixtime() - (60*60*24);
  }
  //Corregir tiempo del intervalo de dias que se restaron del tiempoUnix
  now = now.unixtime() + (interval)*(60*60*24);
  //Eliminar archivos que no esten en la lista de archivos permitidos
  File carpeta = SPIFFS.open("/dataFiles");
  File file = carpeta.openNextFile();
  while(file){
    boolean found = false;
    for(JsonVariant v : allowFiles) {
      if(v.as<String>() == file.name()){
        //Encontrado y salir del loop for
        Serial.println("OK "+ String(file.name()));
        found = true;break;
      }
    }
    //Eliminar el archivo si no se encontro
    if(!found){
      Serial.println("Eliminando "+ String(file.name()));
      SPIFFS.remove(file.name());      
    }
    //Abrir el siguiente archivo
    file = carpeta.openNextFile();
  }

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
    lastTime = now;
    now = rtc.now();
    String text = "";//text se ocupa para guardar en formato csv y respuesta json del websocket
    StaticJsonDocument<256> doc;
    JsonObject root = doc.to<JsonObject>();

    //Si alguna de las fechas cambiaron sera necesario reiniciar el dispositivo
    if(now.year() != lastTime.year() || now.month() != lastTime.month() || now.day() != lastTime.day()){
      ESP.restart();
    }

    //Recolectar la fecha y hora
    root["fecha"] = now.timestamp(DateTime::timestampOpt::TIMESTAMP_DATE);
    text += now.timestamp(DateTime::timestampOpt::TIMESTAMP_DATE); text += ',';
    root["hora"] = now.timestamp(DateTime::timestampOpt::TIMESTAMP_TIME);
    text += now.timestamp(DateTime::timestampOpt::TIMESTAMP_TIME); text += ',';

    //Recolectando datos del acelerometro
    s = sizeof(acelerometroPins) / sizeof(acelerometroPins[0]);
    for(uint8_t i = 0; i < s; i++){
      //Calcular el promedio de lo recolectado del dataDelay con el delayFactor
      aceletrometroData[i] = (aceletrometroData[i] / delayCounter);
      aceletrometroData[i] = acelerometroEcuacion(aceletrometroData[i]);
      //Enviar y Vaciar el dato
      root["aceletrometro"+String(i)] = String(aceletrometroData[i], 4);
      text += String(aceletrometroData[i], 4); text += ',';
      aceletrometroData[i] = 0.0;
    }
    //Recolectando datos de la licor
    s = sizeof(licorPins) / sizeof(licorPins[0]);
    for(uint8_t i = 0; i < s; i++){
      //Calcular el promedio de lo recolectado del dataDelay con el delayFactor
      licorData[i] = (licorData[i] / delayCounter);

      //Enviar y Vaciar el dato
      root["licor"+String(i)] = String(licorData[i], 4);
      text += String(licorData[i], 4); //text += ',';
      licorData[i] = 0.0;
    }

    //Guardar el dato en formato CVS en el dia de hoy si ya paso 1 minuto
    if(now.minute() > lastTime.minute()){
      String filename = "/dataFiles/" + now.timestamp(DateTime::timestampOpt::TIMESTAMP_DATE) +".txt";      
      File f = SPIFFS.open(filename, FILE_APPEND);
      if(!f.println(text)){
        Serial.println("No se ha podido escribir");
      }
      f.close();
    }
    //Vaciar el text para poder mandar la respuesta por el websocket
    text = "";

    serializeJson(doc, text);
    ws.textAll(text.c_str());
    //Resetear el counter para poder Enviar otra vez la respuesta
    delayCounter = 0;
  }  
}