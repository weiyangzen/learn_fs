# File Research: sources/os/plan9/9front/sys/src/9/ppc/uartsaturn.c

Implements a Plan 9 `PhysUart` driver for two memory-mapped Saturn UARTs on PPC. It defines register layout, baud/parity/stop/bits programming, interrupt handling, console selection from `console`, and debug output helpers (`dbgputc`, `dbgputs`, `dbgputx`).

The driver exposes `saturnphysuart` with standard UART callbacks. Receive interrupts drain `rxb` while `Lsr_rxavail` is set; transmit interrupts disable `Ier_txempty` until `uartkick` stages more bytes. FIFO, modem control, RTS, DTR, and break are stubs.

Notable details: UART A/B base addresses are derived from `Saturn`; `subaud` only programs divisor registers when `uart->enabled`; `sukick` loops up to `Txsize` but breaks after writing one byte, effectively single-byte kick despite the size constant.
