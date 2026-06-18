# File Research: sources/os/plan9/9front/sys/src/9/imx8/dat.h

Role: i.MX8 platform data declarations and machine/process structures for the 9front ARM64 kernel.

Key contents:
- Defines time constants (`HZ`, `MS2HZ`, `TK2SEC`) and GPIO interrupt mode constants.
- Declares platform typedefs including `Conf`, `Mach`, `Proc`, `Page`, `PTE`, `Tval`, and `KMap`.
- Defines A.OUT magic, saved label format, FPU save/allocation state, and FP state values.
- Defines memory configuration structures and the global `Conf`.
- Defines `MMMU` with top-level user page-table pointer and `PMMU` with per-process page-table free/head/tail arrays, ASID, and TPIDR.
- Includes shared `portdat.h`, then defines `Mach` with fields known to assembly followed by `PMach`.
- Declares global `active` CPU state, `MACHP()`, and register globals `m`/`up`.
- Defines parsed ISA configuration and device-port structures.

Dependencies:
- Paired with `mem.h` and `l.s`; early `Mach` field offsets are assembly-sensitive.
- Pulls in the common Plan 9 port data model.

Notes:
- `NCOLOR` is fixed to 1; cache virtual color issues are ignored on this platform.
