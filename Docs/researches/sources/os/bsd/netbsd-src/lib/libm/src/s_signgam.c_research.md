# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_signgam.c

Defines the global `int signgam = 0` used by legacy gamma/lgamma APIs.

Key behavior: provides storage for sign reporting.

Important dependencies: `math.h` and `math_private.h`.

Notable risks: global mutable state has the usual thread-safety/ABI implications, though this file only defines it.
