# sources/user-network-fs/samba/source3/modules/vfs_readahead.c

## Purpose
`vfs_readahead.c` issues kernel readahead hints for reads at configured boundaries. It targets clients that issue large sequential reads, especially Vista-era AIO patterns, so later reads may hit warm cache.

## Important APIs, Types, And Functions
- `struct readahead_data` stores `off_bound`, `len`, and a once-only warning flag.
- `readahead_sendfile()` and `readahead_pread()` trigger Linux `readahead()` or `posix_fadvise(POSIX_FADV_WILLNEED)` when `offset % off_bound == 0`.
- `readahead_connect()` allocates per-handle data and reads `readahead:offset` and `readahead:length`.
- `free_readahead_data()` frees the heap allocation.

## Control Flow
On connect, defaults are established: offset boundary defaults to `0x80000`, and length defaults to the boundary. Sendfile and pread wrappers inspect offsets and issue the platform hint only at exact boundaries before delegating to the next VFS operation. Unsupported platforms log one warning per connection path.

## State And Persistence
State is per VFS handle and freed on disconnect. The module changes no files; it only influences kernel cache behavior.

## Dependencies And Integration Points
It depends on Linux `readahead` or POSIX fadvise availability, Samba VFS `pread`/`sendfile`, and loadparm size parsing. It registers as `readahead`.

## Risks
- If `readahead:offset` resolves to zero after parsing but before defaulting incorrectly, modulo-by-zero would be dangerous; current code defaults zero to `0x80000`.
- Workloads with random boundary-aligned reads may cause wasted I/O.
- The module assumes `handle->data` is initialized by connect before read hooks are called.

## Test Signals
- With Linux support, trace `readahead(fd, offset, len)` at configured boundaries.
- With fadvise-only support, trace `posix_fadvise`.
- Verify no hint occurs for non-boundary offsets.
- Verify unsupported builds log the warning only once per handle.
