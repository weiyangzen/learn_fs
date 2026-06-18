# File Research: sources/local-fs/xfsprogs/libxfs/buf_mem.c

Implements memory-backed `xfs_buftarg` support using xfiles and direct `mmap`.

Key responsibilities:
- Initializes xmbuf page-size block geometry and mmap-count limits.
- Allocates and frees memory-backed buffer targets.
- Maps xfile pages directly into `xfs_buf` objects.
- Integrates with the generic cache via xmbuf cache operations.
- Verifies memory-backed daddrs against xfile size.
- Finalizes ephemeral buffers by punching stale pages or running structure verifiers.
- Detaches memory-backed buffers from transactions without disk writeback.

Important behavior:
- Only system page-size blocks are supported.
- `/proc/sys/vm/max_map_count` is used to cap simultaneous mappings; fallback is 1024.
- When mapping pressure or ENOMEM occurs, `xmbuf_unmap_early` causes buffers to unmap on cache put and remap on get.
- Direct-mapped buffers are marked uptodate and unchecked after mmap.

Dependencies:
- Uses xfile, cache, kmem, libxfs buffer, transaction, verifier, and fallocate/mmap APIs.

Notable risks:
- Caller is expected to provide concurrency management.
- Mapping count handling switches global behavior for all xmbufs once pressure is detected.
- Verifier failures in `xmbuf_finalize` indicate memory/software corruption in ephemeral metadata staging.
