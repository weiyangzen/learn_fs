# File Research: sources/os/plan9/9front/sys/src/9/bcm/i2cgpio.c

GPIO bit-banged I2C bus implementation for BCM platforms.

Key responsibilities:
- Drives SDA/SCL with GPIO direction changes, using input as released/high and output as pulled low.
- Implements start, restart, stop, bit read/write, byte read/write, ACK/NACK handling, and clock stretching.
- Registers the bit-banged bus through `addi2cbus()`.
- Uses `microdelay()` for bus timing.

Important behavior:
- Clock stretching waits for SCL to rise with a timeout.
- `io()` handles combined write/read packets, including repeated starts when both output and input lengths are present.
- NACK or stretch timeout terminates the transfer and sends stop.

Dependencies:
- GPIO direction/input/output helpers, Plan 9 I2C core, and kernel delay routines.
