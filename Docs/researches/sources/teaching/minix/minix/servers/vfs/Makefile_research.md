# File Research: sources/teaching/minix/minix/servers/vfs/Makefile

Build file for the MINIX Virtual File System server.

Key contents:
- Builds program `vfs`.
- Source list covers the main VFS subsystems: dispatch, open/read/write, pipes, device maps, paths, devices, mounts, links, exec, descriptors, stat/dir, protection, time, locks, misc, select, tables, vnode/vmnt, request, threading, communication, coredump, block/char/socket devices, and socket maps.
- Adds `gcov.c` and `-DUSE_COVERAGE` when coverage is enabled.
- Uses strict warning settings: `-Wall -Wextra -Wno-sign-compare -Werror`.
- Links `libsys`, `libtimers`, `libexec`, and `libmthread`.
- Uses `<minix.service.mk>`.
