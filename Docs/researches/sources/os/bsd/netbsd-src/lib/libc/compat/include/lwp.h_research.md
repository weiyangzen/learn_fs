# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/lwp.h

Declares compatibility lightweight-process park APIs.

It exposes `_lwp_park` with `timespec50`, `___lwp_park50` with `timespec`, and `___lwp_park60` with clock id/flags plus `timespec`.

This is time ABI compatibility for threading primitives.
