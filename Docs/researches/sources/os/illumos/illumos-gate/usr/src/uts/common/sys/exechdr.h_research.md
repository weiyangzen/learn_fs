# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exechdr.h

## Role

`exechdr.h` defines the historical Sun/UNIX `struct exec` a.out-style executable header and related magic and machine-type constants known by kernel and user programs.

## Definitions

- `struct exec` stores dynamic flag, tool version, machine type, magic, text/data/bss/symbol sizes, entry point, and relocation sizes.
- Defines magic values `OMAGIC`, `NMAGIC`, and `ZMAGIC`.
- Defines legacy machine types for old Sun-2, 68010, 68020, and SPARC executables.
- Defines tool-version constants `TV_SUN2_SUN3` and `TV_SUN4`.
