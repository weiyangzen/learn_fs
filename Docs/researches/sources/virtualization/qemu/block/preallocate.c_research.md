# File Research: sources/virtualization/qemu/block/preallocate.c

## Purpose
Implements QEMU's `preallocate` block filter. The filter sits above a child node and preallocates additional zeroed space when writes extend beyond the known file end, reducing repeated small file extensions.

## Main Entry Points
- `preallocate_open()` opens the child, parses `prealloc-align` and `prealloc-size`, initializes invalid cached state, and configures supported write/zero flags.
- `preallocate_close()` cancels the resize-drop BH and truncates the child back to the real data size when valid.
- `preallocate_reopen_prepare()`, `preallocate_reopen_commit()`, and `preallocate_reopen_abort()` handle option changes and read-only reopen behavior.
- `preallocate_co_pwritev_part()` and `preallocate_co_pwrite_zeroes()` call `handle_write()` before forwarding writes.
- `preallocate_co_truncate()` reconciles explicit user truncation/preallocation with filter-owned preallocation.
- `preallocate_set_perm()` and `preallocate_child_perm()` manage exclusive write/resize permissions and cached state validity.

## Internal Mechanics
The state tracks three boundaries:
- `data_end`: real logical data end as exposed by the filter.
- `zero_start`: start of a trailing region known to read as zero.
- `file_end`: actual child file length, including filter-owned preallocation.

When a write crosses `data_end`, `handle_write()` updates `data_end`, checks whether the write crosses `file_end`, and if needed issues `bdrv_co_pwrite_zeroes()` with `BDRV_REQ_NO_FALLBACK | BDRV_REQ_SERIALISING | BDRV_REQ_NO_WAIT` from an aligned preallocation start to an aligned preallocation end. Zero writes can be merged with the preallocation request when flags permit.

The filter keeps exclusive write and resize permissions on the child while its cached boundaries are valid. When parents no longer need write+resize, a bottom half drops extra preallocation by truncating to `data_end`, invalidates cached state, and refreshes child permissions.

## Dependencies
Uses QEMU block filter APIs, coroutine I/O, child permission callbacks, QemuOpts runtime parsing, bottom halves, and sector/request-alignment rules.

## Filesystem/Block Relevance
This filter changes allocation behavior without changing visible guest data. It is relevant for sparse-file growth, write-zeroes behavior, and the distinction between logical disk length and physically preallocated trailing zero space.

## Risks and Notes
- Cached state is valid only while the filter has exclusive child write and resize permissions.
- Errors during delayed resize dropping leave the filter holding exclusive permissions indefinitely.
- Preallocation requires aligned `prealloc-align`; it must align to both 512 bytes and the child request alignment.
- The filter reports `data_end` as length, not `file_end`, hiding trailing preallocated space from users.
- Explicit truncation with non-falloc modes may first drop filter-owned preallocation so the requested operation has the expected semantics.
