# File Research: sources/os/bsd/netbsd-src/lib/libarch/Makefile

Top-level `libarch` build makefile. It includes per-architecture make fragments for `alpha`, `arm`, `i386`, `m68k`, `powerpc`, `sparc`, and `x86_64`, accumulates sources/assembly objects, and defines `_KERNTYPES`.

If `SRCS` is defined for the current machine, it builds an architecture-specific library named after `LIBC_MACHINE_CPU` or `MLIBDIR`; otherwise it only builds manpages. It uses per-library `shlib_version` and export-symbol files.
