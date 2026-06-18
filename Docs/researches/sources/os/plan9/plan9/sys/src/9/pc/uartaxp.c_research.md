# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartaxp.c

Purpose: `PhysUart` driver named `AvanstarXp` for Avanstar Xp PCI multiport UART cards. The card runs downloaded control firmware and exposes a global control block plus per-channel control blocks in mapped local memory.

Main structures:
- `Gcb`: global control block with command/status words, service request bitmaps, board type, control program version, and CCB layout metadata.
- `Ccb`: per-channel control block with baud/data/line protocol, input/output circular buffer descriptors, modem/error/status fields, and command/status words.
- `Cc`: embeds `Uart` and tracks channel number, CCB pointer, and controller.
- `Ctlr`: PCI device, mapped registers/memory, GCB pointer, interrupt mask, and up to 16 channels.

Key logic:
- `axppnp` scans PCI communication devices for AvanstarXp ID `114f:6001`.
- `axpalloc` maps PCI runtime registers and local memory, resets the adapter, downloads `uartaxpcp` firmware from `uartaxp.i`, starts it, waits for ready, validates board type, and builds channel `Uart`s.
- `axpenable` enables interrupts when requested, asserts DTR/RTS, configures modem control ownership, sets output low watermark, and enables Tx/Rx.
- `axpdisable` drops DTR/RTS, disables Tx/Rx, flushes buffers, and unregisters interrupt when no channels remain enabled.
- `axpinterrupt` handles global doorbell interrupts and atomically drains input, output, command, modem, and error service request bitmaps with `xchgw`.
- `axprecv` drains the card input ring into `uartrecv`; `axpkick` fills the output ring from staged UART output.
- Control methods implement baud, bits, stop, parity, break, modem control, RTS/DTR, FIFO no-op, and status reporting.

Dependencies and integration:
- Implements Plan 9 `PhysUart axpphysuart`.
- Uses `devuart` helpers (`uartrecv`, `uartkick`, `uartstageoutput`), PCI/MMIO mapping, interrupt registration, and the bundled firmware array `uartaxpcp`.

Risks and notes:
- Correct operation depends on downloading and starting card firmware successfully.
- Channel commands either busy-wait before interrupts are enabled or sleep on command service interrupts afterward.
- Error-service handling appears to read `cc->ccb->ms` while checking communication errors, which is unusual because error bits are defined for `ces`.
