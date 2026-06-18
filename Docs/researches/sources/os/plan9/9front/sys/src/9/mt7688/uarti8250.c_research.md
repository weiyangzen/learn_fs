# File Research: sources/os/plan9/9front/sys/src/9/mt7688/uarti8250.c

This is the MT7688 8250-like UART driver adapted for memory-mapped 32-bit UART registers. It defines UART register and bit constants, a `Ctlr` with memory-mapped `io`, IRQ, sticky register cache, FIFO state, and one console UART named `uartL`.

The `PhysUart i8250physuart` methods implement status reporting, FIFO control, DTR/RTS/modem control, parity/stop/bits configuration, fixed baud reporting, break, transmit kick, interrupt handling, enable/disable, polling getc/putc, and console init. `uartconsinit` chooses this UART as `consuart` and configures `115200 8N1`.

`i8250interrupt` drains modem, TX-empty, RX-data, line-status, and timeout interrupt causes, updates UART error counters, sends received bytes into the generic UART layer, and restarts transmit output.

Filesystem relevance is indirect but important for console I/O, diagnostics, boot interaction, and serial-backed device files. Console reliability affects debugging filesystem boot and namespace failures.

Notable risks: baud programming is compiled out, so actual hardware speed is assumed preconfigured; only one UART instance is registered; register access uses word indexing through `u32int*` rather than byte I/O.
