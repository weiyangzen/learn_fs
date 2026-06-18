# File Research: sources/os/plan9/9front/sys/src/cmd/aux/usbsdmux.c

`usbsdmux` controls a USB-SD-Mux-like device by sending SCSI/vendor raw commands to an I2C GPIO expander at address `0x41`. Modes are `off`, `dut`, and `host`, with an optional raw device path defaulting to `/dev/sdUdca10/raw`.

`wr` sends a command header, writes register/value data, then reads textual status and requires zero. The program first disconnects all paths, configures all GPIO pins as outputs, sleeps 100 ms, then applies the selected output pattern.

GPIO bits represent data, power, DUT, and card switching lines. Failures in command writes, data writes, status reads, or nonzero status are fatal.
