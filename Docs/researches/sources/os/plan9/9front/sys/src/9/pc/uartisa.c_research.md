# File Research: sources/os/plan9/9front/sys/src/9/pc/uartisa.c

## Role

ISA discovery wrapper that creates additional 8250-compatible UARTs from kernel configuration.

## Main Interfaces

- Exports `PhysUart isaphysuart` named `UartISA`.
- PnP callback `uartisapnp()` scans `uart2` through `uart5` ISA configuration entries.

## Key Behavior

- Accepts config entries with type `isa`, nonzero port, and nonzero IRQ.
- Defaults frequency to `1843200` if unspecified.
- Allocates I/O port space, creates a controller with `i8250alloc()`, allocates a `Uart`, and binds it to `i8250physuart`.
- Names created ports `COM3` and above based on controller number.

## Dependencies And Assumptions

- Depends entirely on the generic 8250 implementation for runtime behavior.
- Uses `isaconfig()` and `ioalloc()`; it does no probing beyond configured resources.

## Research Notes

- This file is discovery glue, not a UART implementation.
- `isaphysuart` has only `.pnp`; all operational callbacks are nil because returned UARTs use `i8250physuart`.
