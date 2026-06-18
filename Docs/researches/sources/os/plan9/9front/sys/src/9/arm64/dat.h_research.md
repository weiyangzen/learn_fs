# File Research: sources/os/plan9/9front/sys/src/9/arm64/dat.h

ARM64 machine data definitions shared by kernel C code.

Key definitions:
- Time constants, GPIO mode values, and common typedefs.
- `Label`, FPU save/allocation structures, and per-process FPU state.
- `Conf` and `Confmem` memory/process configuration structures.
- Per-machine MMU state with top-level user page table pointer.
- Per-process MMU state with page-table freelists and ASID/TPIDR tracking.
- ARM64 `Mach` layout, including the assembly-known prefix fields.
- `ISAConf`, debug macros, and device resource descriptors.

Dependencies:
- Includes `../port/portdat.h` after architecture-specific type definitions.

Research notes:
- `Mach` register bindings declare `m` in `R27` and `up` in `R26`.
- `PMMU` encodes ASID and user TLS state needed by `trap.c` and `mmu.c`.
