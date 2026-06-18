# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/makefile

Purpose: Standalone upstream-style makefile for building gdtoa outside the NetBSD libc build.

Core behavior:
- Builds generated `arith.h` with `arithchk.c`.
- Builds generated `gd_qnan.h` with `qnan.c`.
- Compiles the gdtoa source list into `gdtoa.a`.
- Provides optional `Printf` target and `xsum.out` source integrity check.
- Provides `clean` target for generated headers, objects, archive, and checksum files.

Dependencies:
- Assumes `cc`, `ar`, and optional `ranlib`.
- Lists the upstream source distribution files in `xs0`.
