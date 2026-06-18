# File Research: sources/os/linux/linux/fs/erofs/Makefile

Builds EROFS core and optional feature objects.

Key behavior:
- Core objects are `super.o`, `inode.o`, `data.o`, `namei.o`, `dir.o`, and `sysfs.o`.
- Adds xattr, compression, algorithm-specific decompressors, crypto acceleration, file-backed I/O, fscache, and inode-sharing objects according to Kconfig options.

Important interactions:
- Mirrors the feature gates defined in `Kconfig`.
