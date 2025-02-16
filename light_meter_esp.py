from machine import ADC, Pin, I2C
from time import sleep, time
import sh1106

W, H = 72, 40
X0, Y0 = 30, 12

# Ініціалізація сенсора
sensor_pin = ADC(Pin(2))
sensor_pin.atten(ADC.ATTN_11DB) # Діапазон до 3.6 В

# Налаштування I2C
i2c = I2C(0, scl=Pin(6), sda=Pin(5))

# Ініціалізація дисплея
oled = sh1106.SH1106_I2C(X0+W, (Y0+H+7) & 0xf8, i2c, rotate=180)
oled.init_display()
oled.contrast(255)

# Піни для кнопок
iso_button = Pin(1, Pin.IN, Pin.PULL_UP) # Кнопка для зміни ISO
aperture_button = Pin(0, Pin.IN, Pin.PULL_UP) # Кнопка для зміни діафрагми
enable_button = Pin(3, Pin.IN, Pin.PULL_UP) # Кнопка для активації ESP

# Попередньо задані значення
iso_values = [50, 100, 200, 250, 400, 800, 1600]
aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

# Початкові значення
iso_index = 1 # Починаємо з ISO 100
aperture_index = 3 # Починаємо з f/2

# Таймер для відстеження активності
start_time = None

def read_button(button):
    """
    Перевірка натискання кнопки та очікування відпускання.
    """
    if button.value() == 0:
        sleep(0.2)  # Антидребезг
        while button.value() == 0:
            sleep(0.01)  # Очікуємо поки кнопку відпустять
        return True
    return False

while True:
    oled.fill(0)
    # Перевірка кнопки активації
    if read_button(enable_button):
        print("ESP активовано. Запуск роботи.")
        start_time = time()

    # Якщо ESP не активовано, переходимо в глибокий сон
    if start_time is None:
        print("Очікування активації...")
        sleep(1)
        continue

    # Перевірка кнопок для зміни ISO та діафрагми
    if read_button(iso_button):
        iso_index = (iso_index + 1) % len(iso_values) # Циклічне перемикання ISO

    if read_button(aperture_button):
        aperture_index = (aperture_index + 1) % len(aperture_values) # Циклічне перемикання діафрагми

    # Поточні значення
    ISO = iso_values[iso_index]
    aperture = aperture_values[aperture_index]

    # Зчитуємо значення з сенсора
    light_level = sensor_pin.read() # Вихід від 0 до 4095
    voltage = light_level * (3.3 / 4095) # Напруга в Вольтах

    # Розрахунок витримки
    shutter_speed = (aperture ** 2) / (voltage * (ISO / 100)) if voltage > 0 else float('inf')
    if shutter_speed > 1:
        shutter_display = f"{shutter_speed:.1f} сек"
        oled.text(f"{shutter_speed:.1f} s", X0, Y0)
        oled.hline(X0, Y0+10, X0+30, Y0+10)
    else:
        shutter_display = f"1/{int(1/shutter_speed)} сек"
        oled.text(f"{shutter_speed:.1f} s", X0, Y0)
        oled.hline(X0, Y0+10, X0+30, Y0+10)

    # Виведення результатів
    print(f"ISO: {ISO}, Діафрагма: f/{aperture}, Рекомендована витримка: {shutter_display}")
    oled.text(f"f/{aperture}", X0, Y0+15)
    oled.hline(X0, Y0+25, X0+30, Y0+25)
    oled.text(f"{ISO} iso", X0, Y0+30)
    oled.show()
    print("-" * 40)

    # Перевірка часу активності
    if time() - start_time > 30:
        print("Час вичерпано. Перехід у глибокий сон.")
        sleep()

    sleep(0.1) # Затримка для стабільнішого зчитування
