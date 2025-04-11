# micro_python

All components code in less number of lines and inbuild python modules

###### Current used (I): DC

Direct current (DC) is one-directional flow of electric charge

**Voltage (V):3~12 v**

* 3v- led bulbs, sensors
* 5v-motors,LCD disply.microcontrollers,LED strip

* 12v- car battery power

**Resistors (R):**

To reduce  voltage in certain amount resistors are used irrespective to output

* IR=V

**Voltage regulator:**

To obtain fixed output irrespective to input. unused voltage will converted as heat rejection.

buck convertor (stepup/stepdown),zenor diode

**Capacitors (optional):**

To store energy and enable smooth start and stop. normally used in motors to reduce noice

**Transistor:**

A transistor is a miniature semiconductor that regulates or controls current or voltage flow

Bipolar junction transistor (BJT)-NPN or PNP

## components description

| item                  | model        | voltage  | prize    | description            |
| --------------------- | ------------ | -------- | -------- | ---------------------- |
| LED diode             | 2 pin        | 3v       | ~1 rupee | -                      |
| RGB diode             | 4 pin        | 3v       | ~3 rs    | -                      |
| Addressable LED strip | ws2812B      | 5v       | ~1000rs  | 5 meters<br />300 leds |
| 16X2 LCD disply       |              | 5v       | ~100rs   | without i2c            |
| i2c module            |              | 5v       | ~50rs    |                        |
| OLED                  | ssd1306-0.96 | 3v       | ~250 rs  |                        |
| OLED                  | ssd1306-0.91 | 3v       | ~150 rs  |                        |
| Hbridge               | L298N        | 5v/5-24v | ~200 rs  |                        |
| Hbridge               | MX1508       | 5v       | ~40 rs   |                        |
| Hbridge               | TA6586       | 5v       | ~100 rs  |                        |
