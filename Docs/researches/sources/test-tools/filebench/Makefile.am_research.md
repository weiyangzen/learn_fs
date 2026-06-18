# sources/test-tools/filebench/Makefile.am

## Purpose
`Makefile.am` is the Automake build manifest for Filebench. It declares the generated parser header, subdirectories, the `filebench` executable, the complete source/header list, distribution extras, yacc/lex flags, conditional warning flags, and preprocessor definitions.

## Important APIs, Types, and Functions
Important Automake variables are `libdir`, `SUBDIRS`, `BUILT_SOURCES`, `bin_PROGRAMS`, `filebench_SOURCES`, `EXTRA_DIST`, `ACLOCAL_AMFLAGS`, `AM_YFLAGS`, conditional `AM_CFLAGS`, and `DEFS`.

## Control Flow and State
Automake expands this manifest into Makefile rules that build parser artifacts, compile all listed core modules plus cvar Mersenne Twister code, link `filebench`, recurse into `workloads` and `cvars`, and install workload library data under `@libdir@/filebench`.

## Persistence and Dependencies
Persistent build state includes generated parser files, objects, the `filebench` binary, and installed library/workload files. Dependencies: Autoconf/Automake, lex/yacc, generated `config.h`, Filebench source modules, and platform definitions such as `_LARGEFILE64_SOURCE` and `_GNU_SOURCE`.

## Integration Points, Risks, and Test Signals
Integration is the central build contract for Filebench. Risks include a long manually maintained source list, duplicate `config.h` in `filebench_SOURCES`, warning flags only under `GCC_USED`, and build failures if generated parser headers are stale. Test signals are `make distcheck`/Automake generation success and a linked `filebench` binary including `aslr.c`.
