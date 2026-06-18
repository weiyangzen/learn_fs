# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/Makefile

## Scope

Build file for OpenBSD `ifconfig`.

## Build Role

- Builds `PROG=ifconfig` with sources `ifconfig.c`, `brconfig.c`, and `sff.c`.
- Installs manual page `ifconfig.8`.
- Links `libutil` and `libm`.

## Dependencies

This file is outside the filesystem utilities but included in the group. It defines only build composition and library dependencies for the networking configuration tool.
