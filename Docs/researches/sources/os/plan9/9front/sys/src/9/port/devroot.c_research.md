# File Research: sources/os/plan9/9front/sys/src/9/port/devroot.c

Purpose: Implements the synthetic root device `#/`, including fixed root directories and boot-file storage.

Key logic:
- Maintains two bounded `Dirlist`s: root entries and `/boot` entries.
- `rootreset` adds standard root directories including `bin`, `dev`, `env`, `fd`, `mnt`, `net`, `proc`, `srv`, and 9front’s `shr`.
- `addbootfile` adds immutable boot files under `/boot`.
- `rootgen`, `rootwalk`, `rootstat`, and `rootread` serve directory entries and file contents from in-memory tables.
- Writes always fail; removal/wstat use default device rejection.

Dependencies and integration:
- Used early by the kernel namespace and boot process; external boot code calls `addbootfile`.

Risks and notes:
- Entry arrays are fixed at 32 root files and 32 boot files; overflow panics.
- Boot file contents are served by pointer without copying in `addbootfile`.
