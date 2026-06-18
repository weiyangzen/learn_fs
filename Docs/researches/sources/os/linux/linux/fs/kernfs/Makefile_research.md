# File Research: sources/os/linux/linux/fs/kernfs/Makefile

Build rules for kernfs.

Key responsibilities:
- Adds kernfs core objects to `obj-y`: `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o`.

Important interactions:
- Builds kernfs as part of the core kernel object set when `fs/kernfs` is included by configuration.

Invariants and risks:
- Object list must remain synchronized with kernfs internal symbol dependencies.
