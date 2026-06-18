# File Research: sources/teaching/xv6-public/uart.c

Intel 8250 UART driver.

Key behavior:
- Initializes COM1 for 9600 baud, 8 data bits, no parity, receive interrupts.
- Detects absent UART if line status reads `0xFF`.
- Enables COM1 IRQ through IOAPIC and prints `xv6...\n`.
- `uartputc` polls transmit readiness with bounded delay and writes one byte.
- `uartgetc` returns one received byte or `-1`.
- `uartintr` feeds UART input into console input handling.

Role:
- Provides serial console output/input alongside CGA/keyboard.
