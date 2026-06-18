# File Research: sources/os/plan9/9front/sys/src/9/zynq/uartzynq.c

Implements the Zynq UART physical driver used by the Plan 9 UART layer.

Key responsibilities:
- Defines register offsets and status bits for the Zynq UART.
- Instantiates one console UART, `UART1`, mapped at `VMAP`, IRQ `UART1IRQ`, default baud `115200`.
- `uartconsinit` binds this UART as `consuart` and configures line mode.
- `zuartkick` drains staged output into the TX FIFO.
- `zuartintr` handles RX trigger and TX empty interrupts, acknowledges interrupt status, feeds received characters to `uartrecv`, and restarts output.
- `zuartenable` waits for TX idle, disables interrupts, programs RX FIFO trigger level, and enables RX/TX interrupts if requested.
- Provides polling `getc/putc`, data-bit selection, parity control, and stubs for unsupported modem/control operations.

Notable details:
- `zuartbaud` only prints the requested baud and returns success; actual divisor programming is absent.
- `zuartparity` appears to use direct bit manipulation of the UART mode register and is the only parity implementation.
