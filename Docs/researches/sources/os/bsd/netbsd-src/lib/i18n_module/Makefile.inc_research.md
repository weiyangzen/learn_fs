# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile.inc

Common build include for i18n modules. It disables lint, profiling, and PIC installation, allows clang warnings without hard failure, and points all modules at the shared `shlib_version`.

It installs modules under `/usr/lib/i18n` or `/usr/lib/${MLIBDIR}/i18n`, adds libc citrus include paths, defines `LOCALEMOD_MAJOR`, sets `BASENAME`, `LIB`, and default `SRCS`, and adds `.PATH` entries for libc citrus module sources.
