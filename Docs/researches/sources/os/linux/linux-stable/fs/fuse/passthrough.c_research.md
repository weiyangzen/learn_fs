# File Research: sources/os/linux/linux-stable/fs/fuse/passthrough.c

## Purpose
Implements FUSE passthrough operations that route reads, writes, splice, and mmap to a kernel backing file while preserving FUSE inode state updates.

## Key Interfaces
- `fuse_passthrough_read_iter()` and `fuse_passthrough_write_iter()` delegate buffered/direct file I/O.
- `fuse_passthrough_splice_read()` and `fuse_passthrough_splice_write()` delegate splice paths.
- `fuse_passthrough_mmap()` maps the backing file.
- `fuse_passthrough_open()` opens a per-FUSE-file backing file.
- `fuse_passthrough_release()` drops the opened backing file and credentials.

## Control Flow And Behavior
Operations fetch `ff->passthrough` and call backing-file helpers with a `backing_file_ctx` carrying the FUSE daemon credentials. Reads and mmap invalidate/update atime through `fuse_file_accessed()`. Writes and splice writes hold the FUSE inode lock and update FUSE write attributes through `fuse_passthrough_end_write()`.

## Dependencies
Uses Linux backing-file helpers, splice helpers, FUSE file private data, FUSE backing ID lookup, credentials, and inode attribute update helpers.

## Risks And Invariants
`backing_id` must be positive and resolvable. Each FUSE file gets its own opened backing file so path/accounting context is per open. Release must drop both file and credential references.
