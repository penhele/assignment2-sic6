from machine import Pin, I2C, ADC
import dht
import time
import ssd1306
import network
import urequests
import json

# Konfigurasi ubidots
UBIDOTS_TOKEN = "BBUS-NTjGslkvecXmt5SO0Ek98CVhkB7yEz"  

# Konfigurasi sensor
sensor = dht.DHT11(Pin(15))
pir_pin = Pin(13, Pin.IN)
mic = ADC(Pin(32))  
mic.atten(ADC.ATTN_11DB)  
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
led = Pin(2, Pin.OUT)
SUARA_THRESHOLD = 2000

# Konfigurasi WiFi
WIFI_SSID = "stephen"
WIFI_PASSWORD = "siapanamamu"

# Konfigurasi Endpoint
ENDPOINT_URL = "http://53e8-112-215-238-132.ngrok-free.app/iot_data"  

# Fungsi koneksi
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())
    return sta_if.ifconfig()[0]

# Fungsi kirim MongoDB
def send_data_to_server(data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(ENDPOINT_URL, data=json.dumps(data), headers=headers)
        print("Server Response:", response.text)
        response.close()
    except Exception as e:
        print("Error sending data to server:", e)

# Fungsi kirim Ubidots
def send_data_to_ubidots(data):
    try:
        url = f"https://industrial.api.ubidots.com/api/v1.6/devices/esp32-uni458" 
        headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
        response = urequests.post(url, data=json.dumps(data), headers=headers)
        print("Ubidots Response:", response.status_code)
        response.close()
    except Exception as e:
        print("Error sending data to Ubidots:", e)

# Fungsi utama
def motion_detected():
    count = 0
    for _ in range(5):
        count += pir_pin.value()
        time.sleep(0.1)
    return count >= 3

ip_address = connect_wifi()

while True:
    try:
        sensor.measure()
        suhu = sensor.temperature()
        kelembaban = sensor.humidity()
        gerakan = 1 if motion_detected() else 0
        nilai_suara = mic.read()

        if gerakan or nilai_suara > SUARA_THRESHOLD:
            led.value(1)
        else:
            led.value(0)

        print("Suhu: {:.2f}°C".format(suhu))
        print("Kelembaban: {:.2f}%".format(kelembaban))
        print("Gerakan terdeteksi!" if gerakan else "Tidak ada gerakan")
        print("Suara: {}".format(nilai_suara))

        oled.fill(0)
        oled.text("Suhu: {:.2f}C".format(suhu), 0, 0)
        oled.text("Kelembaban: {:.2f}%".format(kelembaban), 0, 10)
        oled.text("Gerakan: {}".format(gerakan), 0, 20)
        oled.text("Suara: {}".format(nilai_suara), 0, 30)
        oled.text(f"IP: {ip_address}", 0, 40)
        oled.show()

        data = {
            "suhu": suhu,
            "kelembaban": kelembaban,
            "gerakan": gerakan,
            "suara": nilai_suara,
        }

        send_data_to_server(data)  
        send_data_to_ubidots(data)  

    except OSError as e:
        print("Gagal membaca sensor:", e)

    time.sleep(5)