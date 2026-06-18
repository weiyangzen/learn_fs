# File Research: sources/os/plan9/plan9/sys/src/9/port/mkrootc

Purpose: rc generator that emits C code linking embedded boot-file data into the kernel.

Key logic:
- Arguments are repeated triples: `name cname file`.
- Emits standard kernel includes.
- Declares `extern uchar <cname>code[];` and `extern ulong <cname>len;`.
- Emits `bootlinks()` that calls `addbootfile(name, cnamecode, cnamelen)` for each boot file.

Dependencies and integration:
- Paired with `mkrootall` output and used by generated `mkbootrules`.

Risks and notes:
- It parses filenames only to emit names/symbols; actual file contents are embedded elsewhere.
