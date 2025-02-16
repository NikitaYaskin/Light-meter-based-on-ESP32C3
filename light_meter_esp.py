from machine import ADC, Pin, I2C
from time import sleep, time
import sh1106

W, H = 72, 40
X0, Y0 = 30, 12

# Sensor initialization
sensor_pin = ADC(Pin(2))
sensor_pin.atten(ADC.ATTN_11DB) # Range to 3.6 V

# I2C settings
i2c = I2C(0, scl=Pin(6), sda=Pin(5))

# Display initialization
oled = sh1106.SH1106_I2C(X0+W, (Y0+H+7) & 0xf8, i2c, rotate=180)
oled.init_display()
oled.contrast(255)

# Button pins
iso_button = Pin(1, Pin.IN, Pin.PULL_UP) # ISO change button
aperture_button = Pin(0, Pin.IN, Pin.PULL_UP) # Aperture button
enable_button = Pin(3, Pin.IN, Pin.PULL_UP) # ESP activation button

# Preset values
iso_values = [50, 100, 200, 250, 400, 800, 1600]
aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

# Initial values
iso_index = 1 # Starting with ISO 100
aperture_index = 3 # Starting with f/2

# Activity tracking timer
start_time = None

def read_button(button):
    """
    Перевірка натискання кнопки та очікування відпускання.
    """
    if button.value() == 0:
        sleep(0.2)  # Anti-fragmentation
        while button.value() == 0:
            sleep(0.01)  # We wait until the button is released.
        return True
    return False

while True:
    oled.fill(0)
    # Checking the activation button
    if read_button(enable_button):
        print("ESP активовано. Запуск роботи.")
        start_time = time()

    # If ESP is not activated, we go into deep sleep
    if start_time is None:
        print("Очікування активації...")
        sleep(1)
        continue

    # Checking the ISO and aperture buttons
    if read_button(iso_button):
        iso_index = (iso_index + 1) % len(iso_values) # ISO cycling

    if read_button(aperture_button):
        aperture_index = (aperture_index + 1) % len(aperture_values) # Cyclic aperture switching

    # Current values
    ISO = iso_values[iso_index]
    aperture = aperture_values[aperture_index]

    # Reading the value from the sensor
    light_level = sensor_pin.read() # Output from 0 to 4095
    voltage = light_level * (3.3 / 4095) # Voltage in Volts

    # Shutter speed calculation
    shutter_speed = (aperture ** 2) / (voltage * (ISO / 100)) if voltage > 0 else float('inf')
    if shutter_speed > 1:
        shutter_display = f"{shutter_speed:.1f} сек"
        oled.text(f"{shutter_speed:.1f} s", X0, Y0)
        oled.hline(X0, Y0+10, X0+30, Y0+10)
    else:
        shutter_display = f"1/{int(1/shutter_speed)} сек"
        oled.text(f"{shutter_speed:.1f} s", X0, Y0)
        oled.hline(X0, Y0+10, X0+30, Y0+10)

    # Output of results
    print(f"ISO: {ISO}, Діафрагма: f/{aperture}, Рекомендована витримка: {shutter_display}")
    oled.text(f"f/{aperture}", X0, Y0+15)
    oled.hline(X0, Y0+25, X0+30, Y0+25)
    oled.text(f"{ISO} iso", X0, Y0+30)
    oled.show()
    print("-" * 40)

    # Checking activity time
    if time() - start_time > 30:
        print("Час вичерпано. Перехід у глибокий сон.")
        sleep()

    sleep(0.5) # Delay for more stable reading
