# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vwscanf.c

Read completely: 58 lines.

Implements `vwscanf()` and `vwscanf_l()` as direct wrappers around `vfwscanf(stdin, ...)` and `vfwscanf_l(stdin, loc, ...)`.

The file contains no parser logic; it is the standard-input wide scanning adapter.
