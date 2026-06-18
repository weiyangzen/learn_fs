# File Research: sources/os/plan9/9front/sys/src/9/ppc/dat.h

PowerPC machine-dependent kernel type and global declarations.

Key responsibilities:
- Defines architecture-specific `Label`, floating-point save state, process FP state values, memory configuration, and MMU process state.
- Includes the shared `portdat.h` after defining machine-dependent types.
- Provides a fake `KMap` implementation using direct `KZERO` mapping.
- Defines `Mach` layout, including offsets known by `l.s`, MMU sweep fields, clock frequencies, CPM frequencies, and kernel stack tail.
- Defines `ISAConf`, interrupt vector control `Vctl`, and global `active` machine state.
- Declares `mach0`, register variables `m` and `up`, and initial FP state.

Dependencies:
- Must stay layout-compatible with PPC assembly routines and shared kernel headers.
