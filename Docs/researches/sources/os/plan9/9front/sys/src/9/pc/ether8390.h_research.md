# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8390.h

Header and x86 I/O glue for DP8390-family drivers.

Primary role:
- Defines `Dp8390`, shared constants, exported DP8390 core functions, and PC-specific register/data-port access helpers used by `ether8390.c` and board drivers such as `etherec2t.c`.

Key contents:
- `Dp8390` embeds a `Lock` and stores I/O base, data port, transfer width, shared-memory flag, dummy-remote-read flag, RX ring page pointers, TX busy/page state, multicast address shadow, and multicast hash reference counts.
- `Dp8390BufSz` is `256`, matching DP8390 page size.
- Exports:
  - `dp8390reset(Ether*)`
  - `dp8390read(Dp8390*, void*, ulong, ulong)`
  - `dp8390getea(Ether*, uchar*)`
  - `dp8390setea(Ether*)`

x86-specific helpers:
- `regr(c, r)` reads a byte register from `ctlr->port + r`.
- `regw(c, r, v)` writes a byte register.
- `rdread()` reads remote-DMA data port using `inss` for width 2 or `insb` for width 1.
- `rdwrite()` writes remote-DMA data port using `outss` for width 2 or `outsb` for width 1.
- Unsupported widths panic.

Research notes:
- This header is intentionally architecture-specific; the common core includes it and relies on these macros/functions being present.
- The structure is the contract board drivers must fill before calling `dp8390reset()`.
