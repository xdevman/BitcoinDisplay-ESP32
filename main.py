import network
import usocket
from time import sleep
import urequests
from machine import Pin, I2C
import ssd1306


i2c = I2C(-1, scl=Pin(22), sda=Pin(21)) #For ESP32: pin initializing
#i2c = I2C(-1, scl=Pin(5), sda=Pin(4))  #For ESP8266: pin initializing
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


ssid = "WIFISSID"
password = "WIFIPASSWORD"
server_port = 80

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("WiFi Connected!")
    print("IP Address:", wlan.ifconfig()[0])
    btc_price = get_btc_price()
    OLEDdisplay(btc_price)

def start_server():
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server.bind(('0.0.0.0', server_port))

    server.listen(5)
    print("Server Started!")
    return server

def handle_request(client):
    print("NEW Client")
    currentline = ""
    while True:
        try:
            data = client.recv(1024)
            if data:
                request = data.decode('utf-8')
                print(request, end='')
                if "\r\n\r\n" in request:
                    client.sendall(b"HTTP/1.1 200 OK\r\n")
                    client.sendall(b"Content-type:text/html\r\n")
                    client.sendall(b"\r\n")

                    btc_price = get_btc_price()
                    html_code = f"<html><head></head><body>BTC PRICE: {btc_price}</body></html>"
                    
                    client.sendall(html_code.encode('utf-8'))
                    
                    break
        except OSError:
            break
    client.close()
    print("Client Disconnected")
def OLEDdisplay(price):
  oled.text(f"BTC: ", 32, 16) 
  oled.text(f"{price}", 32, 32)
  oled.show()
def get_btc_price():
    url = "https://api.nobitex.ir/v2/orderbook/BTCUSDT"
    response = urequests.get(url)
    data = response.json()
    last_trade_price = data["lastTradePrice"]
    return last_trade_price

def main():
    connect_wifi()
    #server = start_server()
    while True:
        client, addr = server.accept()
        if client:
            handle_request(client)
            
        sleep(0.1)
        
if __name__ == '__main__':
    main()
