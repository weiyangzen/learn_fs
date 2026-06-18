# File Research: sources/os/linux/linux-stable/fs/bfs/Kconfig

This Kconfig entry defines `CONFIG_BFS_FS`.

Behavior:
- Adds tristate “BFS file system support”.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD`.
- Help text describes SCO UnixWare Boot File System, usually mounted at `/stand`, with read/write access from Linux.
- Documents that module builds are named `bfs`.
- Notes that a root filesystem cannot be built as a module.

Integration:
- Controls compilation of `fs/bfs/Makefile`.

Risk notes:
- The help text points users toward UnixWare slice support and BFS documentation.
