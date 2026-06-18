# File Research: sources/os/bsd/freebsd-src/sys/sys/gmon.h

## Purpose
Defines gprof/gmon profiling file structures, kernel profiling state, arc records, and profiling sysctl identifiers.

## Main Interfaces
- `struct gmonhdr`: header for `gmon.out`.
- `GMONVERSION`.
- `HISTCOUNTER` type, controlled by `GPROF4`.
- Profiling sizing constants: `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- Arc structures: `struct tostruct`, `struct rawarc`.
- `struct gmonparam`: profiling buffers, bounds, hash fraction, rate, overhead counters, histogram type.
- Global `_gmonparam`.
- States: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`, `HIRES`.
- Sysctl IDs: `GPROF_STATE`, `COUNT`, `FROMS`, `TOS`, `GMONPARAM`.
- Kernel helpers/macros: `KCOUNT`, `PC_TO_I`, optional `GUPROF` calibration/profiling functions, `kmupetext`, `mexitcount`, etc.
- Userland functions: `moncontrol`, `monstartup`.

## Dependencies And Integration
Includes `machine/profile.h` for function alignment and pointer-sized profiling types. Kernel support exposes profiling data through sysctl.

## Risk Notes
Several sizing macros depend on architecture function alignment. `MAXARCS` is constrained by `u_short` link storage. Structure layouts are consumed by profiling tools.
