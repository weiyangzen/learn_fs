# File Research: sources/os/plan9/9front/sys/src/9/pc/uartpci.c

## Role

PCI discovery wrapper for selected 8250-compatible serial cards and serial-over-LAN devices.

## Main Interfaces

- Exports `PhysUart pciphysuart` named `UartPCI`.
- PnP callback `uartpcipnp()` scans PCI communication devices and creates UARTs backed by `i8250physuart`.

## Key Behavior

- `uartpci()` maps I/O BAR space, enables PCI device access, allocates `n` UART records, and creates one `i8250` controller per channel using fixed register spacing.
- Supports StarTech, Oxford/OxSemi, SIIG, Perle PCI-Fast/Ultraport, PLX-bridged serial cards, Intel AMT SOL, and Intel chipset KT controller IDs.
- Handles subsystem-ID-based card selection for generic Oxford and PLX bridge devices.
- `ultraport16si()` performs extra register writes to put Ultraport16si channels into RS-232 mode before binding them.

## Dependencies And Assumptions

- Depends on PCI config access, I/O BAR allocation, and `i8250alloc()`.
- Only supports I/O-port BARs, not MMIO UART register blocks.
- Device support is ID-table-driven and conservative.

## Research Notes

- Like `uartisa.c`, this is enumeration/binding glue over `uarti8250.c`.
- The global `perlehead/perletail` list is used as the accumulated returned UART chain for all matched PCI devices.
