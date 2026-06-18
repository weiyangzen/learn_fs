# File Research: sources/os/bsd/freebsd-src/sbin/routed/Makefile

Purpose: FreeBSD build definition for the `routed` RIP daemon.

Behavior:
- Builds `PROG=routed` in package `rip`.
- Uses source files `if.c`, `input.c`, `main.c`, `output.c`, `parms.c`, `radix.c`, `rdisc.c`, `table.c`, and `trace.c`.
- Installs `routed.8`.
- Links against `libmd`.
- Builds `rtquery` as a subdirectory.
- Includes `bsd.prog.mk`.

Integration: this makefile ties the shared definitions in `defs.h` to the daemon modules that implement interface discovery, RIP input/output, router discovery, route table management, tracing, and parameter parsing.

Risk notes: warning level is `WARNS?=3`, reflecting older C code style. Build is specific to FreeBSD’s system make infrastructure.
