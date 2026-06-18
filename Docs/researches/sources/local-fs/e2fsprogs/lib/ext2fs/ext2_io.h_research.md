# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_io.h

## Purpose
Declares the ext2fs IO abstraction layer: `io_channel`, `io_manager`, statistics, flags, helper wrappers, and available backends.

## Key Structures
- `struct_io_channel`: open channel state, manager pointer, block size, error callbacks, refcount, flags, alignment, private/app data.
- `struct_io_stats`: bytes read/written and cache hit/miss counters.
- `struct_io_manager`: backend vtable for open/close, block IO, byte writes, options, stats, 64-bit block IO, discard, readahead, zeroout, and flock.

## APIs and Flags
- Channel flags include writethrough, discard-zeroes, block-device, threads, nodiscard, and nozeroout.
- Open flags include RW, exclusive, direct IO, force bounce, threads, and nocache.
- Lock flags support exclusive/shared/trylock.
- Convenience macros call through the manager vtable.
- Declares wrappers such as `io_channel_read_blk64`, `io_channel_write_blk64`, `io_channel_discard`, `io_channel_zeroout`, `io_channel_alloc_buf`, and flock helpers.

## Backends
Declares platform/default managers:
- `windows_io_manager` on Windows.
- `unix_io_manager`, `unixfd_io_manager` elsewhere.
- `sparse_io_manager`, `sparsefd_io_manager`.
- `undo_io_manager`.
- `test_io_manager` and test callbacks.

## Risks and Notes
- 64-bit block operation availability matters for large filesystems; lack of support maps to ext2fs errcodes.
- Error callbacks allow callers to intercept partial/failed IO.
- All disk metadata readers and writers depend on this abstraction.
