# File Research: sources/os/bsd/dragonflybsd/sys/sys/linker_set.h

Defines ELF linker set macros. `__MAKE_SET` places pointers into named `set_*` sections and declares start/stop symbols. Public macros include `TEXT_SET`, `DATA_SET`, `BSS_SET`, `ABS_SET`, `SET_ENTRY`, `SET_DECLARE`, `SET_BEGIN`, `SET_LIMIT`, `SET_FOREACH`, `SET_ITEM`, and `SET_COUNT`.

This is core infrastructure for `SYSINIT`, module metadata, and other registry-style kernel tables, including VFS/module registration.
