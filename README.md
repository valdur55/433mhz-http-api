**W.I.P / DRAFT**

This project is for replacing remote control for 433mhz remote controllable switches.
In later edition, I added IFFIT to control Wi-Fi light bulb (SONOFF B5)

**Why I made this project:**

I had a dream which involved a command named "öö" ("night") which included suspending the laptop, shutting down monitors and lighting up a light bulb near bed.
I already had remote controllable switches in place.

**Process of making this project:**

I opened the remote control and measured voltage for button control, and it was 12V, which I couldn't use with Arduino/Raspberry Pi.

The next step was to find another solution for emulating button pressing. For that reason I ordered 433mhz receiver and transmitter, sniffed codes with Arduino's RCSwitch module and built a web app for triggering scenes with REST API requests.

While working with the main part, I decided to add possibility to delay light. In real life testing, I decided to do light switches as priority.

Main UI for controlling this system is rofi (rofi's role as window for searching commands)
Later on I added icons for mobile phone main screen and even shortcuts for smartwatch.

Finally, I added shortcuts for taskbar elements.

For example, volume control mouse keybindings are:
```
scroll up = volume +
scroll down = volume -
middle button = mute/unmute
back = speakers power off
forward = speakers power on
```



**Remote control channels**
~~~~
Channel 1 is computer monitors
Channel 2 is computer desk light
Channel 3 is speakers
Channel 4 is bad light
~~~~


