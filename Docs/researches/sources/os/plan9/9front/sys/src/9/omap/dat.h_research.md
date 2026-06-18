# File Research: sources/os/plan9/9front/sys/src/9/omap/dat.h

Core machine data declarations for the OMAP kernel.

Key contents:
- Time constants, `HZ`, and timer conversion macros.
- Forward declarations and typedefs for core kernel types.
- `Label`, `FPsave`, `PFPU`, `Confmem`, `Conf`, `MMMU`, `PMMU`, and `Mach` definitions.
- Per-process MMU state and per-machine stack/register/cache/timing state.
- Global CPU/proc register bindings: `m` in R10 and `up` in R9.
- ISA-style config structure used by generic drivers.
- `Memcache` cache-description structure populated by `cacheinfo`.
- DMA mode constants: post-increment, constant, indexed, and double-indexed.

Research notes:
- The OMAP port is uniprocessor here: `MAXMACH` is 1 in `mem.h`, and structures reflect that.
- FPU save state is soft/emulated-oriented and stores control/status plus register space.
