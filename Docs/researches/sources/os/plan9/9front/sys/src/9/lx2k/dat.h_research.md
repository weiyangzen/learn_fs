# File Research: sources/os/plan9/9front/sys/src/9/lx2k/dat.h

LX2K ARM64 machine data definitions. It defines `Conf`, `Confmem`, FPU save state, process and machine MMU state, `Mach`, `ISAConf`, device config structures, hardware register types, and extern-register bindings for `m` and `up`.

The platform uses ARM64 FP/SIMD state (`FPalloc` with 32 128-bit registers), a `PFPU` state model, and a page-table based `MMMU`/`PMMU` design with ASIDs. `Mach` includes MMU top-level pointer, FPU state, CPU type/frequency fields, and Plan 9 per-machine data.

Notable risks: `MAXSYSARG`, AOUT magic, FPU state constants, and MMU fields must match shared port code and assembly trap-frame conventions.
