# File Research: sources/os/plan9/9front/sys/src/9/teg2/fns.h

Function declarations and macros for the Tegra/ARM port. It imports portable Plan 9 declarations, declares ARM/Tegra cache, clock, interrupt, MMU, FPU, PCI, UART, screen, CPU, coprocessor, timer, and architecture hooks, and maps legacy `intrenable`/`intrdisable` to GIC `irqenable`/`irqdisable`.

Defines `cycles`, `KADDR`, `PADDR`, `getpgcolor`, no-op `kmapinval`, and `MASK`. It is the central declaration bridge between C files, assembly routines, and portable kernel code.
