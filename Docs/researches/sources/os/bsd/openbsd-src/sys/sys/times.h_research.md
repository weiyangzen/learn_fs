# File Research: sources/os/bsd/openbsd-src/sys/sys/times.h

Defines the POSIX `struct tms` CPU accounting result for `times(3)`: user/system CPU time for the process and terminated children. It defines `clock_t` via `sys/_types.h` if not already present.

Outside the kernel it declares `clock_t times(struct tms *)`. This header is pure ABI surface with no kernel implementation details beyond avoiding the userland prototype under `_KERNEL`.
