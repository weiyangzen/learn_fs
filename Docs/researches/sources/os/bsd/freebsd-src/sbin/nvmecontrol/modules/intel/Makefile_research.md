# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/Makefile

Builds the Intel `nvmecontrol` vendor module.

Key contents:
- `LIB=intel`.
- `SRCS=intel.c`.
- Includes `bsd.lib.mk`.

Research notes:
- Relies on module-wide common settings from the parent include path/build environment.
