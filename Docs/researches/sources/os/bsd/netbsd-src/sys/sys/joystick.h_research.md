# File Research: sources/os/bsd/netbsd-src/sys/sys/joystick.h

Small joystick device ioctl header. It defines `struct joystick` with X/Y axis and two button fields, plus ioctls to set/get timeout and X/Y offsets.

The interface is simple and depends on `sys/ioctl.h` command encoding. Main risks are legacy ABI expectations and the comment typo on `JOY_SET_Y_OFFSET`; behavior is determined by the device driver implementation.
