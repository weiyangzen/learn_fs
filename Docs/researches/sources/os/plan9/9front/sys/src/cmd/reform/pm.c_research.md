# File Research: sources/os/plan9/9front/sys/src/cmd/reform/pm.c

MNT Reform power-management filesystem. Exposes `/dev/battery`, `/dev/cputemp`, `/dev/light`, `/dev/kbdoled`, and `/dev/pmctl`.

Controls LCD PWM brightness, keyboard backlight, trackball LEDs, keyboard OLED image upload, CPU temperature sensor setup/readout, LPC battery/firmware/voltage queries over SPI, and poweroff requests.

Uses HID control discovery through `/dev/usb/ctl`, raw HID commands for keyboard/trackball, memory-mapped hardware segments for TMU/PWM/SPI, and a request queue for potentially slow LPC reads with flush support.
