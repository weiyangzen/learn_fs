# File Research: sources/os/plan9/9front/sys/src/9/cycv/uartcycv.c

Role: Cyclone V console UART driver for a single 16550-like UART instance.

Key responsibilities:
- Defines UART register offsets and line/status bits.
- Instantiates one controller at `UART_BASE` with `UART0IRQ`.
- Registers one Plan 9 `Uart` named `UART1`, default 115200 baud, console enabled.
- Implements polling `getc`/`putc`, interrupt receive/transmit handling, and staged output kicking.
- Enables UART interrupts and basic 8-bit line/fifo setup in `vuartenable()`.
- Supports word size and parity changes by mutating `LCR`; baud changes only print requested baud and return success.
- Exposes `PhysUart cycvphysuart`.

Dependencies:
- Uses common Plan 9 UART framework (`uartrecv`, `uartstageoutput`, `consuart`) and platform interrupt registration.

Notes:
- Stop bits, RTS/DTR/break/fifo/power/modem control are no-op or unsupported.
- Transmit writes through `RBR` offset, matching 16550 THR/RBR shared register layout.
