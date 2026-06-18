# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-end.mak

Late Unix makefile fragment for directory setup, debug/profile builds, config header generation, and tags.

Key points:
- Defines `STDDIRS` to create binary, generated, and object directories for graphics and interpreter components.
- Defines `PGDIRS` / `PGDEFS` / `pg` / `pgclean` for profiling builds.
- Defines `DEBUGDIRS` / `DEBUGDEFS` / `debug` / `debugclean` for debug builds.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Provides an `etags` target over graphics and PostScript source headers.

Dependencies and interactions:
- Included near the end of Unix top-level makefiles.
- Uses `ECHOGS_XE`, `TOP_MAKEFILES`, `USE_ASM`, `FPU_TYPE`, and path variables set earlier.

Research relevance:
- Captures build variants and generated platform constants for Unix Ghostscript builds.
