# File Research: sources/os/bsd/freebsd-src/sys/sys/joystick.h

Small user-visible joystick ioctl header. `struct joystick` reports x/y axis values and two button states.

Ioctls allow setting/getting timeout and setting/getting X/Y offsets using group `'J'`.
