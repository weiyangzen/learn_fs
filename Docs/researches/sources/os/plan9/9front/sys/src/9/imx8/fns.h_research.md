# File Research: sources/os/plan9/9front/sys/src/9/imx8/fns.h

Role: i.MX8 platform function declarations tying C code to common port code, assembly routines, and platform drivers.

Key contents:
- Includes common `portfns.h`.
- Declares assembly functions from `l.s`: barriers, atomics, interrupt priority, user transition, FPU register access, SMC call, TLB operations, cache maintenance, cycle counters, TTBR/FAR access.
- Declares MMU/memory APIs such as `paddr`, `kaddr`, `kmap`, `mmukmap`, `vmap`, `mmuidmap`, `mmu0init`, `meminit`, and `ucalloc`.
- Declares clock/timer, FPU, trap, IRQ, sysreg, UART, DMA, main/config, CCM, GPC, LCD, IOMUX, GPIO, and PCIe APIs.
- Defines `GPIO_PIN(n, m)` encoding as bank shifted by 5 plus pin.

Dependencies:
- Signature contract used across all i.MX8 files and port code.

Notes:
- The function declarations for GPIO interrupt enable/disable omit `extern` but are still declarations.
