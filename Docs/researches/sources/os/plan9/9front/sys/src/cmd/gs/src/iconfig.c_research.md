# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iconfig.c

Builds configuration-dependent interpreter tables.

Key points:
- Content matches `iconf.c`.
- Defines default main-instance values.
- Builds init-file and emulator-name ref arrays from `gconf.h`.
- Builds function type, operator definition, and plugin instantiation tables.
- Terminates generated arrays with sentinel entries.

Research notes:
- This appears to be a duplicate or alternate build-name variant of `iconf.c`.
- Its role is configuration-table generation, not runtime algorithm implementation.
