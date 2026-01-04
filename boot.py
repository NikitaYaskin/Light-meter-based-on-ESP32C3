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

# Піни для кнопок (Тепер тільки дві кнопки)
iso_button = Pin(1, Pin.IN, Pin.PULL_UP)
aperture_button = Pin(0, Pin.IN, Pin.PULL_UP) # Ця кнопка тепер і активує пристрій

# Попередньо задані значення
iso_values = [50, 100, 200, 250, 400, 800, 1600]
aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

# Початкові значення
iso_index = 1 
aperture_index = 3 

# Таймер для відстеження активності (None означає, що пристрій "спить")
start_time = None

def read_button(button):
    if button.value() == 0:
        sleep(0.1)  # Антидребезг (трохи зменшено для кращого відгуку)
        if button.value() == 0:
            while button.value() == 0:
                sleep(0.01)
            return True
    return False

while True:
    # 1. Очікування активації через aperture_button
    if start_time is None:
        oled.fill(0)
        oled.text("PRESS BTN", X0, Y0 + 15)
        oled.show()
        
        if read_button(aperture_button):
            print("Пристрій активовано через кнопку діафрагми.")
            start_time = time()
            # Важливо: ми не змінюємо aperture_index при першому натисканні, 
            # щоб просто "прокинутись" на збереженому значенні
        continue

    # 2. Робота активованого пристрою
    oled.fill(0)

    # Зміна ISO
    if read_button(iso_button):
        iso_index = (iso_index + 1) % len(iso_values)
        start_time = time() # Оновлюємо таймер активності при натисканні

    # Зміна діафрагми
    if read_button(aperture_button):
        aperture_index = (aperture_index + 1) % len(aperture_values)
        start_time = time() # Оновлюємо таймер активності при натисканні

    ISO = iso_values[iso_index]
    aperture = aperture_values[aperture_index]

    # Розрахунок
    light_level = sensor_pin.read()
    voltage = light_level * (3.3 / 4095)

    # Формула експонометрії
    shutter_speed = (aperture ** 2) / (voltage * (ISO / 100)) if voltage > 0.01 else 999
    
    if shutter_speed >= 1:
        shutter_display = f"{shutter_speed:.1f}s"
    else:
        shutter_display = f"1/{int(1/shutter_speed)}"

    # Виведення на дисплей
    oled.text(shutter_display, X0, Y0)
    oled.hline(X0, Y0+10, 60, 1)
    oled.text(f"f/{aperture}", X0, Y0+15)
    oled.hline(X0, Y0+25, 60, 1)
    oled.text(f"ISO {ISO}", X0, Y0+30)
    oled.show()

    # 3. Перевірка тайм-ауту (30 секунд)
    if time() - start_time > 30:
        print("Час вийшов. Повернення в режим очікування.")
        start_time = None 
        oled.fill(0)
        oled.show()

    sleep(0.1)
