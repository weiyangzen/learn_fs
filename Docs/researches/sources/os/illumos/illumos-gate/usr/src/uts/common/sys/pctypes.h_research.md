# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pctypes.h

## Purpose
Defines shared PCMCIA primitive types and little-endian conversion helpers.

## Main Interfaces
- `irq_t`: IRQ level type.
- `baseaddr_t`: memory base address pointer type.
- `ioaddr_t`: `uint32_t` on x86, `caddr_t` on SPARC.
- `intrfunc_t`: interrupt callback signature returning `uint32_t`.
- `acc_handle_t`: opaque data access handle.
- `leshort()` and `lelong()`: byte-swap on big-endian systems, identity on little-endian systems.

## Dependencies And Relationships
Depends on base illumos integer/address types being available. Used by PCMCIA and related adapter code that needs architecture-neutral I/O address and endian handling.

## Research Notes
The endian helpers are macro-only and assume their arguments are integer values. `ioaddr_t` intentionally differs between x86 and SPARC.
