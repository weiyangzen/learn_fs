# File Research: sources/os/plan9/9front/sys/src/9/pc64/dat.h

Primary amd64 kernel data-structure header for the 9front PC64 kernel.

Key contents:
- Forward declarations for core kernel, MMU, process, architecture, PCI, PCMCIA, and interrupt structures.
- `Label` scheduler jump context.
- FPU save-state structures for FXSAVE/XSAVE-style state, plus `PFPU` process FPU bookkeeping.
- `Conf` and `Confmem` machine memory/process/image/swap configuration.
- `Segdesc`, `MMU`, and `PMMU` structures for page-table and per-process MMU state.
- Includes `../port/portdat.h`, then defines amd64-specific `Tss`, `Mach`, `PCArch`, CPUID feature bits, MSR numbers, `ISAConf`, global `machp`, register globals `m` and `up`, and `DevConf`.
- `Mach` stores per-CPU scheduler, timing, CPUID, MMU, GDT/TSS, interrupt, FPU, and diagnostic state.
- `PCArch` provides architecture hooks for reset, serial power, NMI, interrupts, clocks, and timers.

Notable dependencies:
- Shared Plan 9 port data model from `portdat.h`.
- `mem.h` constants for CPU counts, page table sizing, and segment selectors.

Research notes:
- This header defines architecture contracts consumed throughout `pc64`.
- It also contains initialized storage for `machp[MAXMACH]`, so it is not purely declarations in the C sense.
