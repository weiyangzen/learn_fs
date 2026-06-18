# File Research: sources/os/plan9/plan9/sys/src/cmd/chmod.c

Implements Plan 9 `chmod` for octal modes and symbolic modes. Octal input is parsed with base 8 and applied against read/write/execute permission bits. Symbolic parsing supports `u`, `g`, `o`, `a`, operators `+`, `-`, `=`, and mode letters `r`, `w`, `x`, `a` append, `l` exclusive, `t` temporary.

For each target it reads the current `Dir`, computes `(old & ~mask) | (mode & mask)`, and writes back with `dirwstat`. It reports individual stat/wstat failures but always exits success unless usage or mode parsing fails.
