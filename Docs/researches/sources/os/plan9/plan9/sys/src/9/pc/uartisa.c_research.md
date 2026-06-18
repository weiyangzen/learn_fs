# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartisa.c

Purpose: ISA bus wrapper `PhysUart` named `UartISA` that discovers configured ISA UARTs and exposes them through the generic i8250 backend.

Key logic:
- `uartisapnp` scans `isaconfig("uart", ctlrno, &isa)` for controller numbers 2 through 5.
- Accepts only entries of type `isa` with nonzero port and IRQ, defaulting frequency to 1.8432 MHz.
- `uartisa` allocates the I/O range, allocates a `Uart`, creates an i8250 controller via `i8250alloc`, names it `COM%d`, and points `uart->phys` at `i8250physuart`.

Dependencies and integration:
- Delegates all runtime UART operations to `i8250physuart`.
- Uses ISA config parsing, I/O allocation, and `i8250alloc`.

Risks and notes:
- The `isaphysuart` vtable contains only `pnp`; returned UARTs must use `i8250physuart` for actual operation.
- Starts at controller number 2, leaving built-in COM1/COM2 to `uarti8250.c`.
