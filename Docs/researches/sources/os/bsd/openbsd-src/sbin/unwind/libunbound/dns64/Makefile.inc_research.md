# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/Makefile.inc

Build fragment for Unbound DNS64 module.

Behavior:
- Adds `.PATH` for `libunbound/dns64`.
- Adds `dns64.c` to `SRCS`.

Role in group:
- Enables DNS64 module compilation in the embedded Unbound source build.
