# File Research: sources/os/bsd/netbsd-src/lib/libc/gmon/Makefile.inc

libc build fragment for profiling support.

Adds:
- Source files: `gmon.c`, `mcount.c`.
- Manpage: `moncontrol.3`, linked as `monstartup.3`.
- Architecture search path `${ARCHDIR}/gmon`.

Special cases:
- MIPS disables assembler warnings for `mcount.c`.
- i386 suppresses a lint diagnostic for `_mcount`.
- i386/x86_64 with GCC >= 6 and clang suppress frame-address warnings.
- `mcount.po` and `gmon.po` are copied from non-profiled object variants because profiling code itself cannot be compiled with profiling.
