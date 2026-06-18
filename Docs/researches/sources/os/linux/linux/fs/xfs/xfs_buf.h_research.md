# File Research: sources/os/linux/linux/fs/xfs/xfs_buf.h

Defines XFS metadata buffer and buffer target structures, flags, verifier interfaces, and public buffer-cache APIs.

Key elements:
- Defines buffer daddr constants `XFS_BUF_DADDR_MAX` and `XFS_BUF_DADDR_NULL`.
- Defines buffer state flags: read, write, read-ahead, async, done, stale, write-fail, log-recovery, kmem-backed, delayed-write queued, livescan, incore, and trylock.
- `struct xfs_buftarg` represents a buffer target/block device with DAX state, sector geometry, LRU/shrinker state, readahead counters, I/O ratelimiting, atomic write unit bounds, and hash table.
- `struct xfs_buf_map` describes one physical I/O segment.
- `struct xfs_buf_ops` provides verifier name, v4/v5 magic values, read/write verify callbacks, and optional structural verifier.
- `struct xfs_buf` stores hash node/key, length, lock/ref state, LRU state, perag/mount/target pointers, backing address, I/O work/completion, log item links, maps, pin count, error/retry state, verifier ops, and RCU head.
- Declares buffer lookup/read/readahead/uncached APIs and inline single-map wrappers.
- Declares hold/release, lock/unlock, synchronous write, I/O error reporting, corrupt marking, stale marking, delayed-write queue/submit helpers, checksum helpers, buftarg allocation/free/drain/configuration, and magic verification.
- Defines inline helpers for incore lookup, get/read/readahead, `xfs_buf_relse`, buffer offsets, zeroing, daddr access, oneshot caching, pin checks, and checksum update/verify.

Dependencies:
- Consumed across XFS metadata code for all block-buffer access and verification.
- Implemented primarily by `xfs_buf.c`.

Research notes:
- `xfs_buftarg` distinguishes metadata sector size from device logical sector size.
- `XBF_LIVESCAN` exists for online fsck cache scanning and changes lookup behavior around stale/nonmatching buffers.
- `xfs_buf_oneshot` marks a buffer disposable after release unless it is already strongly LRU-referenced.
- `xfs_buf_islocked` checks semaphore count directly, matching the buffer lock implementation.
