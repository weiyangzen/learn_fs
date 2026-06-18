# File Research: sources/os/plan9/9front/sys/src/9/arm64/uartqemu.c

QEMU PL011 UART driver for ARM64 console and serial I/O.

Key behavior:
- Defines PL011 register offsets and bit fields.
- Instantiates one UART at `VIRTIO + 0x1000000`, 24 MHz, 115200 baud.
- Handles RX/TX interrupts, FIFO fill/drain, interrupt clearing, and UART enable/disable.
- Implements line control for baud, data bits, stop bits, parity, and break.
- Provides polled `getc`/`putc`.
- Initializes the console UART with `l8 pn s1`.

Dependencies:
- Uses shared UART infrastructure and interrupt registration.

Research notes:
- Derived from the BCM PL011 driver but hardwired to the QEMU ARM64 mapping.
