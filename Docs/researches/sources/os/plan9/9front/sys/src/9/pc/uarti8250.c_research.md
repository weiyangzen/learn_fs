# File Research: sources/os/plan9/9front/sys/src/9/pc/uarti8250.c

## Role

Generic `PhysUart` implementation for 8250-compatible serial ports, including COM1/COM2 defaults and reusable allocation support for ISA/PCI frontends.

## Main Interfaces

- Exports `PhysUart i8250physuart` named `i8250`.
- `i8250pnp()` returns built-in COM1/COM2 UARTs.
- `i8250alloc()` allocates controller state for external ISA/PCI-discovered ports.
- `i8250console()` selects a boot console from the `console` configuration variable.

## Key Behavior

- Implements standard 8250 register access, sticky write state for interrupt/line/modem control, baud divisor programming, parity/stop/data-bit settings, break signaling, DTR/RTS, modem control, and FIFO trigger setup.
- Detects FIFO availability once by enabling FIFO and reading `Iir`.
- Interrupt handler drains modem, transmit-empty, receive-data, line-status, and timeout interrupts until no interrupt is pending.
- Receive path records overrun/parity/framing/break errors and only passes clean non-break bytes to `uartrecv()`.
- Enable path installs interrupts, sets `Ier/Mcr`, asserts DTR/RTS, and manually invokes the interrupt handler to clear stale pending events after PIC reset.

## Dependencies And Assumptions

- Uses I/O port access and Plan 9 UART core helpers such as `uartstageoutput`, `uartkick`, and `uartrecv`.
- Default COM1/COM2 ports are `0x3f8/0x2f8` with IRQs `4/3`.
- FIFO changes can flush receive data; the code waits for transmitter empty but cannot fully protect RX bytes.

## Research Notes

- This is the base implementation reused by `uartisa.c` and `uartpci.c`.
- The driver supports polling `getc/putc` for console use as well as interrupt-driven operation.
