# File Research: sources/os/linux/linux/fs/iomap/trace.h

Defines the iomap tracepoint ABI used internally for diagnostics. The header explicitly states these tracepoints are not stable kernel ABI.

Trace coverage:
- Read/readahead page count events.
- Range events for writeback, release, invalidate, DIO invalidate failure, queued DIO, and zeroing.
- Iomap mapping events for destination and source mappings, including device, inode, address, offset, length, type, flags, and bdev.
- `iomap_add_to_ioend` for writeback aggregation.
- `iomap_iter` for iterator state, flags, ops pointer, and caller.
- Direct I/O begin and completion events, including inode, size, offset, length, `ki_flags`, DIO flags, async status, error, and return value.

It also defines symbolic strings for iomap types, iterator flags, iomap mapping flags, and public DIO flags, then includes `trace/define_trace.h`.
