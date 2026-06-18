# File Research: sources/os/linux/linux-stable/fs/iomap/Makefile

This Makefile builds the iomap library objects according to enabled kernel configuration options.

Key responsibilities:
- Adds include path `-I $(src)` for trace event headers.
- Builds `iomap.o` when `CONFIG_FS_IOMAP` is enabled.
- Always includes `trace.o`, `iter.o`, and `buffered-io.o` in the iomap core object.
- Adds block-backed helpers when `CONFIG_BLOCK` is enabled: `direct-io.o`, `ioend.o`, `fiemap.o`, `seek.o`, and `bio.o`.
- Adds `swapfile.o` when `CONFIG_SWAP` is enabled.

Research notes:
- `buffered-io.c` is part of the core iomap library, while `bio.c` is only built for block-enabled kernels.
