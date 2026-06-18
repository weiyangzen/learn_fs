# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crt0.S

m68k process entry stub. It pushes `%a2` as `ps_strings`, pushes `%a1` as cleanup, and branches to `___start`.

The stub aliases `_start` to `__start` and uses the standard m68k call stack convention.
