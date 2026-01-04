from machine import ADC, Pin, I2C
from time import sleep, time
import sh1106

W, H = 72, 40
X0, Y0 = 30, 12

# Ініціалізація сенсора
sensor_pin = ADC(Pin(2))
sensor_pin.atten(ADC.ATTN_11DB) 

# Налаштування I2C
i2c = I2C(0, scl=Pin(6), sda=Pin(5))

# Ініціалізація дисплея
oled = sh1106.SH1106_I2C(X0+W, (Y0+H+7) & 0xf8, i2c, rotate=180)
oled.init_display()
oled.contrast(255)

# Піни для кнопок
iso_button = Pin(1, Pin.IN, Pin.PULL_UP)
aperture_button = Pin(0, Pin.IN, Pin.PULL_UP)

# Попередньо задані значення
iso_values = [50, 100, 200, 250, 400, 800, 1600]
aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

iso_index = 1 
aperture_index = 3 

# Таймери
start_time = None
last_reading_time = 0  # Час останнього зчитування датчика

def read_button(button):
    if button.value() == 0:
        sleep(0.05) # Швидкий антидребезг
        if button.value() == 0:
            while button.value() == 0:
                sleep(0.01)
            return True
    return False

# При першому запуску вимикаємо екран
oled.fill(0)
oled.show()
oled.sleep(True)

while True:
    current_time = time()

    # 1. Режим очікування
    if start_time is None:
        if read_button(aperture_button):
            print("Активація...")
            oled.sleep(False)
            start_time = current_time
            last_reading_time = 0 # Скидаємо, щоб оновити екран миттєво при прокиданні
        continue

    # 2. Перевірка кнопок (працюють миттєво)
    need_immediate_update = False
    
    if read_button(iso_button):
        iso_index = (iso_index + 1) % len(iso_values)
        start_time = current_time
        need_immediate_update = True # Оновлюємо екран відразу після зміни параметра

    if read_button(aperture_button):
        aperture_index = (aperture_index + 1) % len(aperture_values)
        start_time = current_time
        need_immediate_update = True

    # 3. Зчитування датчика та оновлення екрана (раз на секунду АБО при натисканні кнопок)
    if current_time - last_reading_time >= 1 or need_immediate_update:
        oled.fill(0)
        
        ISO = iso_values[iso_index]
        aperture = aperture_values[aperture_index]

        # Зчитування датчика
        light_level = sensor_pin.read()
        voltage = light_level * (3.3 / 4095)

        # Розрахунок витримки
        shutter_speed = (aperture ** 2) / (voltage * (ISO / 100)) if voltage > 0.01 else 999
        
        if shutter_speed >= 1:
            shutter_display = f"{shutter_speed:.1f}s"
        else:
            shutter_display = f"1/{int(1/shutter_speed)}"

        # Вивід на дисплей
        oled.text(shutter_display, X0, Y0)
        oled.hline(X0, Y0+10, 60, 1)
        oled.text(f"f/{aperture}", X0, Y0+15)
        oled.hline(X0, Y0+25, 60, 1)
        oled.text(f"ISO {ISO}", X0, Y0+30)
        oled.show()
        
        last_reading_time = current_time

    # 4. Автовимкнення
    if current_time - start_time > 30:
        print("Вимкнення екрану.")
        start_time = None 
        oled.fill(0)
        oled.show()
        oled.sleep(True)

    sleep(0.05) # Коротка затримка циклу для високої швидкості реакції кнопокfrom machine import ADC, Pin, I2C
from time import sleep, time
import sh1106

W, H = 72, 40
X0, Y0 = 30, 12

# Ініціалізація сенсора
sensor_pin = ADC(Pin(2))
sensor_pin.atten(ADC.ATTN_11DB) 

# Налаштування I2C
i2c = I2C(0, scl=Pin(6), sda=Pin(5))

# Ініціалізація дисплея
oled = sh1106.SH1106_I2C(X0+W, (Y0+H+7) & 0xf8, i2c, rotate=180)
oled.init_display()
oled.contrast(255)

# Піни для кнопок
iso_button = Pin(1, Pin.IN, Pin.PULL_UP)
aperture_button = Pin(0, Pin.IN, Pin.PULL_UP)

# Попередньо задані значення
iso_values = [50, 100, 200, 250, 400, 800, 1600]
aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

iso_index = 1 
aperture_index = 3 

# Таймери
start_time = None
last_reading_time = 0  # Час останнього зчитування датчика

def read_button(button):
    if button.value() == 0:
        sleep(0.05) # Швидкий антидребезг
        if button.value() == 0:
            while button.value() == 0:
                sleep(0.01)
            return True
    return False

# При першому запуску вимикаємо екран
oled.fill(0)
oled.show()
oled.sleep(True)

while True:
    current_time = time()

    # 1. Режим очікування
    if start_time is None:
        if read_button(aperture_button):
            print("Активація...")
            oled.sleep(False)
            start_time = current_time
            last_reading_time = 0 # Скидаємо, щоб оновити екран миттєво при прокиданні
        continue

    # 2. Перевірка кнопок (працюють миттєво)
    need_immediate_update = False
    
    if read_button(iso_button):
        iso_index = (iso_index + 1) % len(iso_values)
        start_time = current_time
        need_immediate_update = True # Оновлюємо екран відразу після зміни параметра

    if read_button(aperture_button):
        aperture_index = (aperture_index + 1) % len(aperture_values)
        start_time = current_time
        need_immediate_update = True

    # 3. Зчитування датчика та оновлення екрана (раз на секунду АБО при натисканні кнопок)
    if current_time - last_reading_time >= 1 or need_immediate_update:
        oled.fill(0)
        
        ISO = iso_values[iso_index]
        aperture = aperture_values[aperture_index]

        # Зчитування датчика
        light_level = sensor_pin.read()
        voltage = light_level * (3.3 / 4095)

        # Розрахунок витримки
        shutter_speed = (aperture ** 2) / (voltage * (ISO / 100)) if voltage > 0.01 else 999
        
        if shutter_speed >= 1:
            shutter_display = f"{shutter_speed:.1f}s"
        else:
            shutter_display = f"1/{int(1/shutter_speed)}"

        # Вивід на дисплей
        oled.text(shutter_display, X0, Y0)
        oled.hline(X0, Y0+10, 60, 1)
        oled.text(f"f/{aperture}", X0, Y0+15)
        oled.hline(X0, Y0+25, 60, 1)
        oled.text(f"ISO {ISO}", X0, Y0+30)
        oled.show()
        
        last_reading_time = current_time

    # 4. Автовимкнення
    if current_time - start_time > 30:
        print("Вимкнення екрану.")
        start_time = None 
        oled.fill(0)
        oled.show()
        oled.sleep(True)

    sleep(0.05) # Коротка затримка циклу для високої швидкості реакції кнопок
