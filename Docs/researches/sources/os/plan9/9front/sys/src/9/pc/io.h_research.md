# File Research: sources/os/plan9/9front/sys/src/9/pc/io.h

## Purpose
Defines PC interrupt vector constants, interrupt-control structures, bus address macros, and PCMCIA data structures.

## Key Elements
The first enum assigns exception vectors, PIC IRQ vectors, LAPIC offsets, syscall vector `64`, and APIC external vector range. `Vctl` describes one registered interrupt/trap handler, including handler function, argument, ISR/EOI hooks, enable/disable callbacks, IRQ/vector/CPU metadata, and driver name. The file also defines `BUSUNKNOWN`, ISA/PCI address translation macros, EISA constants, and PCMCIA slot/configuration/map structures.

## Dependencies
Uses kernel types such as `Ureg`, `Lock`, `ulong`, `ushort`, `uchar`, and `KNAMELEN`.

## Behavior/Risks
This header is central ABI for interrupt registration. Constants must stay aligned with trap setup, PIC/APIC code, and assembly vector-table assumptions; changing vector numbers or `Vctl` layout would affect multiple low-level subsystems.
