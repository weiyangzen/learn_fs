# File Research: sources/os/plan9/plan9/sys/src/9/teg2/fns.h

Function prototype and macro header for the Tegra 2 Plan 9 kernel port.

Key contents:
- Includes generic port prototypes and declares architecture-specific cache, clock, MMU, interrupt, PCI, DMA, UART, FPU, CPU/SMP, CP15, screen, probe, reboot, and utility functions.
- Defines `intrenable`/`intrdisable` wrappers over GIC `irqenable`/`irqdisable`.
- Declares functions used by `main`, functions called from the generic port layer, and miscellaneous machine-dependent helpers.
- Defines core convenience macros: `cycles`, `waserror`, `KADDR`, `PADDR`, `MASK`, `PTR2UINT`, `UINT2PTR`, `getpgcolor`, and no-op `kmapinval`.

Role:
- This is the cross-file declaration surface for the Tegra port and the bridge between generic Plan 9 port code and machine-dependent implementations.

Notable constraints:
- `cycles(vlp)` is mapped to `lcycles()` and returns a 32-bit value stored through the pointer.
- `waserror()` directly manipulates `up->nerrlab` and `setlabel`, matching Plan 9 kernel error-stack conventions.
- `KADDR`/`PADDR` assume the port's direct physical/virtual mapping scheme.
