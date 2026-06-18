# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartpci.c

Purpose: PCI wrapper `PhysUart` named `UartPCI` that recognizes specific PCI serial adapters and exposes their ports through the generic i8250 backend.

Key logic:
- `uartpcipnp` scans PCI communication devices, including some "other" serial class variants, and matches known StarTech, Oxford, SIIG, PLX/Perle, and Ultraport boards.
- `uartpci` allocates I/O BAR space, creates `n` `Uart` objects, allocates per-port i8250 controller state, assigns per-device frequency, names the ports, and appends them to a global Perle/PCI UART list.
- `ultraport16si` writes board-specific registers to force RS232 mode before exposing 16 ports as i8250-like UARTs.
- Subsystem IDs are used for Oxford and PLX/Perle devices to distinguish board layouts and oscillator frequencies.

Dependencies and integration:
- Delegates all actual serial operations to `i8250physuart`.
- Uses PCI config reads, I/O allocation, `i8250alloc`, and the Plan 9 UART list convention.

Risks and notes:
- Only known device/subsystem IDs are supported; unknown Oxford/Perle variants are printed and skipped.
- Some matched cards expose multiple BARs/port groups and are appended to a shared list.
- The `pciphysuart` vtable only provides `pnp`; returned UARTs use `i8250physuart`.
