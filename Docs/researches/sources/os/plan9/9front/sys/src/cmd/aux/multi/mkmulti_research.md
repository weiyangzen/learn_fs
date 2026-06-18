# File Research: sources/os/plan9/9front/sys/src/cmd/aux/multi/mkmulti

`mkmulti` is an rc build script that creates a combined `multi` binary from multiple Plan 9 commands. For each command name, it emits a renamed `<cmd>_main` prototype into `multiproto.h`, a dispatch entry into `multi.h`, builds the command object files with `mk`, prefixes symbols using `aux/8prefix`, and links all objects with `multi.c`.

It has special handling for `disk/prep` and `disk/fdisk`, tries several build directories and output names, moves generated `.8` objects into numbered `a.N.8` files, and cleans most command directories afterward.

The script depends on Plan 9 toolchain commands: `mk`, `8c`, `8l`, `hoc`, `sed`, `basename`, and `aux/8prefix`. It assumes `/sys/src/cmd` layout and 386 object naming.
