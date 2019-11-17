# Sismografo y Gases (Prototipo2)
Este proyecto se esta llevando acabo para la recolección de lecturas de aceleración de la gravedad
en los ejes X, Y y Z que se utlización para determinar la magnitud de un sismo en un determinado lugar.
Tambien sera capaz de recolectar los datos una Licor 840 que brinda lecturas de CO2 y H2O.

# Modelado de la Base de Datos

![PROFIT!](/resources/esquema.png)

## Componentes
1. ESP32 Devkit V1
2. Licor 840
3. ADS115 I2C
4. Accelerometro ADXL335 con salidas Analogas
4. Otros componentes comunes

## Herramientas de Linux
Se utilizaran las siguientes dependencias para poder realizar la instalación de micropython
```
apt install -y python2.7 python3 python-pip python3-pip python-serial git
pip3 install rshell
```
Se necesitan tambien las herramientas de Espressif del siguiente repositorio:
```
git clone https://github.com/espressif/esptool.git
```

## MicroPython
Se utilizara micropython por el facil acceso a base de datos.
Descargar: https://micropython.org/download
Instalando MicroPython:
```
esptool --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-micropython.bin
```