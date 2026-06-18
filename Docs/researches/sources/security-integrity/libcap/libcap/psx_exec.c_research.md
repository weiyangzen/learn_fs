## sources/security-integrity/libcap/libcap/psx_exec.c

Purpose: executable entry body for `libpsx.so` when run directly.

Important APIs/functions: `SO_MAIN` from `execable.h`.

Control flow: prints the invoked command/library version, license note, and homepage.

State/persistence: no mutable state.

Dependencies/integration: compiled with `LIBRARY_VERSION` and `SHARED_LOADER` into `psx_magic.o` by `libcap/Makefile`.

Risks: depends on executable shared-object machinery; no option handling beyond printing.

Test signals: `./libpsx.so` from `libpsxsotest`.
