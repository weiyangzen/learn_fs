# File Research: sources/os/bsd/netbsd-src/sys/sys/kcore.h

Defines NetBSD kernel crash dump/core file header structures. It provides `KCORE_MAGIC`, `KCORESEG_MAGIC`, physical RAM segment descriptors, a main `kcore_hdr_t`, and per-segment `kcore_seg_t`.

The format is intentionally architecture-shareable by using wide address/size fields. Consumers include crash dump readers and kernel memory inspection tools. Risks are binary format stability, alignment assumptions, and consistent interpretation of `c_midmag` with regular core-file conventions.
