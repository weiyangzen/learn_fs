# File Research: sources/os/bsd/openbsd-src/sys/sys/gmon.h

This header defines gprof/gmon profiling data structures and userspace profiling hooks.

Key definitions:
- `struct gmonhdr` file header and `GMONVERSION`.
- Histogram settings: `HISTCOUNTER`, `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- Arc structures: `struct tostruct`, `struct rawarc`.
- Rounding macros: `ROUNDDOWN`, `ROUNDUP`.
- `struct gmonparam` profiling state with sample buffer, froms, tos, pc bounds, output buffer, raw arcs, dirfd, and list linkage.
- Profiling states: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`.
- Sysctl selectors: `GPROF_STATE`, `COUNT`, `FROMS`, `TOS`, `GMONPARAM`.

Kernel/userland APIs:
- Kernel global: `gmoninit`.
- Userland globals/functions: `_gmonparam`, `_mcleanup`, `_monstartup`, `moncontrol`, `_gmon_alloc`.

Risk notes:
- Profiling buffer sizing depends on text address ranges and architecture profile definitions.
- `MAXARCS` is bounded by the histogram counter width.
