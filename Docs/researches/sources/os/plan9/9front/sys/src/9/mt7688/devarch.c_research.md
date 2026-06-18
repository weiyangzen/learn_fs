# File Research: sources/os/plan9/9front/sys/src/9/mt7688/devarch.c

MT7688 `#P/arch` device implementation. It provides an extensible arch directory with `addarchfile`, standard device attach/walk/stat/open/read/write operations, and two built-in read-only files: `cputype` and `sysctl`.

`cputyperead` reads MIPS PRID/config registers and reports endian mode, CPU family, revision, I/D cache sizes, coherency/write type, TLB entries, FPU presence, and COP2 presence. `sysctlread` reads system-control chip ID, clock gating, and reset registers, then formats per-device clock/reset state using a static gate table.

Notable risks: `chipid` is treated as a string without explicit null termination; the arch directory has a hard maximum of 16 entries.
