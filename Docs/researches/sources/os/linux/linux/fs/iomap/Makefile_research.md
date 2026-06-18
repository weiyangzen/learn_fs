# File Research: sources/os/linux/linux/fs/iomap/Makefile

Kbuild file for the iomap library.

Build behavior:
- Adds `-I $(src)` so trace event headers can include local files.
- Builds `iomap.o` when `CONFIG_FS_IOMAP` is enabled.
- Core object list includes `trace.o`, `iter.o`, and `buffered-io.o`.
- With `CONFIG_BLOCK`, adds direct I/O, writeback completion, fiemap, seek, and bio helpers.
- With `CONFIG_SWAP`, adds swapfile support.

Risk:
- Configuration guards matter: non-block builds still get buffered iomap support, while block-only features are separated.
