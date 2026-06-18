# File Research: sources/os/bsd/freebsd-src/sys/sys/times.h

POSIX `times(3)` CPU accounting ABI header.

Key responsibilities:
- Defines `clock_t` if needed.
- Defines `struct tms` with user/system CPU time for the process and terminated children.
- Declares userland `times(struct tms *)`.

Dependencies:
- Includes `sys/_types.h` and, for userland prototypes, `sys/cdefs.h`.

Notable risks:
- Simple compatibility ABI; field type and order must remain stable for POSIX consumers.
