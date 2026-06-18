# File Research: sources/os/plan9/9front/sys/src/9/lx2k/uartlx2k.c

LX2K PL011 UART driver adapted from BCM2835 code. It defines PL011 register offsets and bits, a single console UART at `VIRTIO+0x11c0000`, and full basic UART methods for enable/disable, interrupt RX/TX, baud, bits, stop, parity, break, getc, and putc.

`enable` disables the UART, registers the GIC interrupt when requested, enables TX/RX interrupts, then turns the UART on. `interrupt` drains RX FIFO, kicks TX, and clears interrupt causes. `baud` programs integer/fractional divisors from a 24 MHz clock.

`uartconsinit` sets `consuart`, marks it as console, applies line settings, and flushes buffered kernel messages.

Notable risks: modem/DTR/RTS/FIFO controls are no-ops; divisor math is simple and tied to the configured 24 MHz clock.
