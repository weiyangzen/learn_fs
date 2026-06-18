# File Research: sources/os/plan9/9front/sys/src/9/bcm/uartpl011.c

ARM PL011 UART driver for BCM platforms.

Key responsibilities:
- Implements Plan 9 `PhysUart` operations for PL011-compatible UARTs.
- Handles RX/TX interrupts, FIFO draining/filling, enable/disable, baud configuration, line control, break, parity, stop bits, and polled I/O.
- Controls UART enable state and interrupt masks safely while changing line settings.

Important behavior:
- Uses integer/fractional baud divisors.
- Updates line-control bits through helper masking.
- Supports common serial settings more fully than mini-UART.

Dependencies:
- Plan 9 UART layer, interrupt registration, PL011 register layout, and BCM clock data.
