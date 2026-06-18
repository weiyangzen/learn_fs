# File Research: sources/virtualization/nbdkit/filters/ext2/io.c

Provides a libext2fs `io_manager` implementation backed by nbdkit `next` callbacks instead of POSIX file descriptors. It is derived heavily from e2fsprogs `unix_io.c`.

`nbdkit_io_encode()` and `nbdkit_io_decode()` encode an `nbdkit_next *` as a pseudo-device name `nbdkit:%p`, allowing `ext2fs_open()` to pass the backend pointer through the libext2fs I/O manager interface.

The private channel state stores magic, backend pointer, offset, and I/O stats. Raw block reads/writes translate ext2 block/count requests into byte offsets and call `next->pread()` or `next->pwrite()`. The manager also implements byte writes, flush, block-size changes, stats, offset option parsing, discard, optional cache readahead, and optional zeroout.

Trim and zero are forwarded only if the underlying plugin advertises support; otherwise libext2fs receives unimplemented errors. Flush is conditional on `next->can_flush()`.
