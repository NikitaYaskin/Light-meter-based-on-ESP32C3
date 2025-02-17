# Light meter based on ESP32-C3 with 0.42 inch Oled screen
An affordable and customizable alternative to expensive modern light meters, allowing you to modify and adapt it to your needs.

## What we neet for this project:
- **ESP32-C3** with 0.42 Oled screen
- **TEMT6000** light sensor
- 3 regular buttons

## Libs
 - [**SH1106**](https://github.com/robert-hh/SH1106) library for working with an OLED screen 
 - **machine** library for working with Pins, ADC and I2C
 - **time** library for managing delays

## Baseline values for ISO and Aperture:
- iso_values      = [50, 100, 200, 250, 400, 800, 1600]
- aperture_values = [1.2, 1.4, 1.8, 2, 2.8, 4, 5.6, 8, 16, 22]

## What is left to do?
- isolate **TEMT6000** light sensor reading from the main while loop
- save the values of **Aperture** and **ISO** in the program
