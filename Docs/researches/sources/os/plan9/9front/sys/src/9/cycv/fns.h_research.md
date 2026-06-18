# File Research: sources/os/plan9/9front/sys/src/9/cycv/fns.h

Cyclone V architecture function declarations and macros.

Key contents:
- Declares atomics, address translation, process context, idle/event, MMU, interrupt, timer, UART, FP, cache, DMA, arch, and screen helpers.
- Defines `KADDR`, `PADDR`, `VA`, `PTR2UINT`, `userureg`, and `getpgcolor`.
- Declares cache-line and range maintenance routines plus physical-address cache helpers.
- Declares `dmacopy()` with DMA attribute arguments.

Role:
- Shared prototype layer connecting Cyclone V assembly, platform code, and Plan 9 port code.
