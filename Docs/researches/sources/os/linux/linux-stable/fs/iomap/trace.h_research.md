# File Research: sources/os/linux/linux-stable/fs/iomap/trace.h

Defines iomap tracepoints. The file explicitly notes these tracepoints are not a stable kernel ABI.

Trace coverage:
- Readpage/readahead events with dev, inode, and page count.
- Generic range events for writeback, folio release/invalidate, DIO invalidate failure, queued DIO, and zeroing.
- Iomap mapping events for destination/source maps with type, flags, bdev, addr, offset, and length.
- `iomap_add_to_ioend` for writeback aggregation decisions.
- `iomap_iter` for iterator position, length, status, flags, ops, and caller.
- `iomap_dio_rw_begin` and `iomap_dio_complete` for direct I/O request and completion state.

String tables:
- Iomap types, iterator flags, iomap mapping flags, and public DIO flags are mapped to readable trace output.
- The trace include path/file footer causes generated trace definitions to come from `trace.c`.
