# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-end.mak

Common near-final Unix makefile fragment for build directories, debug/profile targets, generated variant config, and tags.

Key points:
- Defines `STDDIRS`, `PGDIRS`, and `DEBUGDIRS` to create bin/generated/object directories.
- Defines recursive `pg`, `pgclean`, `debug`, and `debugclean` targets with adjusted flags and output directories.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Adds `TAGS` target using `etags`.

Dependencies and interactions:
- Included late by Unix and Desqview/X configurations.
- Depends on `ECHOGS_XE`, `TOP_MAKEFILES`, and variables set by platform makefiles.

Research relevance:
- Centralizes variant build directory handling and generated compile-time capability constants.
