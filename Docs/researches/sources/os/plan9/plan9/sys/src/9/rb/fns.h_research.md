# File Research: sources/os/plan9/plan9/sys/src/9/rb/fns.h

RouterBOARD/MIPS function prototype and low-level macro header.

Key contents:
- Imports port-level prototypes.
- Declares board, clock, cache, TLB, MMU, trap, FP, PCI, I/O, UART, interrupt, syscall, watchdog, and architecture helper functions.
- Defines `procsetup` as FP initialization.
- Declares register helpers such as CP0 config/status/count/compare, TLB accessors, cache flushes, and assembly process-transition routines.
- Defines `waserror`, `KADDR`, `PADDR`, and `KSEG1ADDR`.

Role:
- Central compile-time contract among MIPS assembly, C platform code, device drivers, and the generic Plan 9 kernel.

Notable risks:
- Prototype mismatches here can hide ABI issues with assembly routines.
- Some declared functions are platform stubs or provided outside this batch.
