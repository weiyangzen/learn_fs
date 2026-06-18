# File Research: sources/virtualization/nbdkit/filters/ext2/io.h

Declares the ext2 filter’s custom libext2fs I/O bridge. It includes `ext2_io.h` and `nbdkit-filter.h`.

Defines `EXT2_ET_MAGIC_NBDKIT_IO_CHANNEL` using a reserved ext2fs magic value. Exports `nbdkit_io_encode()`, `nbdkit_io_decode()`, and the global `io_manager nbdkit_io_manager`.

This header is the narrow interface between `ext2.c` and the backend-backed I/O manager in `io.c`.
