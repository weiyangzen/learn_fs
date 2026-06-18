# File Research: sources/local-fs/f2fs-tools/fsck/Makefile.am

## Purpose
Autotools build definition for the `fsck.f2fs` binary and its symlinked tool modes: `dump.f2fs`, `defrag.f2fs`, `resize.f2fs`, `sload.f2fs`, `f2fslabel`, and `inject.f2fs`.

## Key contents
- Builds `fsck.f2fs` from the fsck tool sources: `main.c`, `fsck.c`, `dump.c`, `mount.c`, `defrag.c`, `resize.c`, `node.c`, `segment.c`, `dir.c`, `sload.c`, `xattr.c`, `compress.c`, quota sources, and `inject.c`.
- Installs private headers used by this tool directory, including `fsck.h`, `f2fs.h`, `dict.h`, quota headers, `compress.h`, `inject.h`.
- Links against configured optional libraries:
  - `libselinux`
  - `libuuid`
  - `liblzo2`
  - `liblz4`
  - `libwinpthread`
  - local `libf2fs.la`

## Integration notes
The multiple installed command names are symlinks to the same executable. Runtime dispatch is therefore expected to happen in `main.c` based on argv/tool name or options.

## Research notes
This file is purely build/install wiring. It establishes that the fsck directory is a multi-tool frontend sharing the same F2FS mount, metadata, directory, quota, compression, dump, resize, defrag, and injection code.
