# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/Makefile

## Purpose
Builds the `ldconfig` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=ldconfig`.
- Compiles `elfhints.c` and `ldconfig.c`.
- Adds include path for `libexec/rtld-elf`.
- Installs `ldconfig.8`.
- Includes `bsd.prog.mk`.
