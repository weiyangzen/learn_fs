# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/Makefile.inc

Read completely: 15 lines.

This make include adds libc's SSP/FORTIFY checked wrapper sources. `SSP_SRCS` lists checked variants for gets/fgets, memory functions, formatted output, string copy/concat functions, and `ssp_redirect.c`; each source is added to `SRCS` with warning level 4.

Important interactions: installs `ssp.3` and `__builtin_object_size.3` manuals and controls whether these fortified entry points are built into libc.

Security/reliability notes: no runtime logic, but this file is the build switchboard for libc's checked-buffer ABI.
