# File Research: sources/local-fs/xfsdump/restore/Makefile

Builds the `xfsrestore` command.

Key structure:
- Defines common headers/sources symlinked from `../common`.
- Defines inventory headers/sources symlinked from `../inventory`.
- Local restore-only sources include `bag.c`, `content.c`, `dirattr.c`, `inomap.c`, `mmap.c`, `namreg.c`, `node.c`, `tree.c`, and `win.c`.
- Links against UUID, handle, attr, remote tape, and pthread libraries.
- Adds `-DRESTORE`, and optionally `-DHAVE_FALLOCATE`.
- Default target builds dependencies and `xfsrestore`.

Install behavior:
- Installs binary under root sbin.
- Also installs/symlinks into package sbin unless both directories are the same filesystem entry.
- Development install is empty.

Role:
- Assembles restore program from shared dump/restore infrastructure, inventory support, librmt, and restore-local modules.
