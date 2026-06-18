# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconf.h

## Purpose
Defines the shared kernel/sysconf utility representation of `/etc/system` entries and module-control command constants.

## Main Interfaces
- `struct sysparam`: linked-list record for parsed `/etc/system` entries, including command type, operation, module name, token/config strings, numeric info, allocated address list, and duplicate/termination flags.
- `struct modcmd`: command-name to command-type mapping.
- Module command constants:
  - `MOD_EXCLUDE`, `MOD_INCLUDE`, `MOD_FORCELOAD`
  - root/swap device and filesystem directives
  - `MOD_MODDIR`, `MOD_SET`, `MOD_SET32`, `MOD_SET64`
- `mod_sysctl()` command constants:
  - `SYS_FORCELOAD`, `SYS_SET_KVAR`, `SYS_SET_MVAR`, `SYS_CHECK_EXCLUDE`
- Assignment operation constants: `SETOP_ASSIGN`, `SETOP_AND`, `SETOP_OR`.

## Dependencies And Relationships
This header is consumed by boot/module configuration code that parses `/etc/system` and later applies kernel/module variable settings or load policy.

## Research Notes
The file is a compact ABI for system configuration parsing. The `SYSPARAM_*` flags distinguish token types, duplicate entries, and terminal list entries.
