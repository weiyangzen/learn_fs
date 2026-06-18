# File Research: sources/os/plan9/9front/sys/src/9/port/mkrootc

C generator for linking embedded boot files into the kernel boot file table.

Key responsibilities:
- Requires argument triples: `name cname file`.
- Emits kernel includes.
- Emits `extern uchar <cname>code[];` and `extern ulong <cname>len;` for every embedded file.
- Emits `bootlinks()` that calls `addbootfile(name, code, len)` for each file.

Role:
- Bridges `mkrootall` assembly data into the runtime boot file registry.
