# File Research: sources/os/bsd/netbsd-src/sys/sys/gmon.h

Read completely: 154 lines.

## Purpose
Defines kernel/user profiling data structures and sysctl identifiers for `gmon` profiling output.

## Main Interfaces
- `struct gmonhdr`: profiling file header.
- `GMONVERSION`.
- `HISTCOUNTER`, `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- `struct tostruct`, `struct rawarc`, `struct gmonparam`.
- `_gmonparam`.
- Profiling states: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`.
- Sysctl selectors: `GPROF_STATE`, `GPROF_COUNT`, `GPROF_FROMS`, `GPROF_TOS`, `GPROF_GMONPARAM`, `GPROF_PERCPU`.

## Dependencies And Integration
Includes machine profiling definitions. Used by profiling instrumentation and kernel sysctl export.

## Risks And Edge Cases
- Arc and histogram sizing trades memory for profiling granularity.
- `MAXARCS` is tied to `HISTCOUNTER` width.

## Filesystem Relevance
Low direct relevance. Profiling can measure filesystem code but does not implement filesystem behavior.
