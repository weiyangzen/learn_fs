# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/Makefile

Builds the WDC `nvmecontrol` vendor module.

Key contents:
- `LIB=wdc`.
- `SRCS=wdc.c`.
- Includes `bsd.lib.mk`.

Research notes:
- The requested group includes only the Makefile, not `wdc.c`; behavior of the WDC module is therefore out of this file’s scope.
