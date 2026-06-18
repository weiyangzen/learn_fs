# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/Makefile

Builds the `swapctl` program from `swapctl.c` and `swaplist.c`.

Key settings:
- `PROG=swapctl`
- `SRCS=swapctl.c swaplist.c`
- Links `-lutil`.
- Installs `swapctl.8`.
- Creates a hard/linked command alias from `swapctl` to `swapon`.

Role:
- Supports both `swapctl` and compatibility `swapon` command behavior from the same binary.
