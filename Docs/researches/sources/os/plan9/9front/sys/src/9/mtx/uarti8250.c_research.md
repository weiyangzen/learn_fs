# File Research: sources/os/plan9/9front/sys/src/9/mtx/uarti8250.c

This is the MTX 8250-compatible serial driver for COM1/COM2 using I/O-port access. It defines two controllers at `0x3F8` and `0x2F8`, IRQs 4 and 3, and a 1.8432 MHz UART clock.

The `PhysUart` methods implement status, FIFO control, DTR/RTS/modem control, parity/stop/bits, baud divisor programming, break, transmit kick, interrupt service, enable/disable, polling getc/putc, and console selection. `i8250console` reads `console` from config, configures default `9600 8N1`, applies any suffix command, enables polling, and marks the chosen UART as console.

`i8250interrupt` handles modem status, TX empty, RX data, and timeout interrupts. It updates UART error counters and passes received bytes to the generic UART layer.

Filesystem relevance is console and serial device support. Serial devices are exposed through Plan 9 device files and are important for boot/debug access.

Notable risks: FIFO detection logic appears inverted or at least old-style (`if(!(Iir & Ife)) ctlr->fifo = 1`); disable does not unregister interrupt once enabled; console speed defaults to 9600 unless config overrides it.
