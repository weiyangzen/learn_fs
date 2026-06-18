# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_rawread.c

Optional FFS raw-read fast path that bypasses the normal buffer cache read path for suitable user reads.

Key responsibilities:
- Defines sysctls `vfs.ffs.allowrawread` and `vfs.ffs.rawreadahead`.
- Initializes a secondary pbuf UMA zone for raw read buffers during VM configuration.
- `ffs_rawread_sync()` ensures raw reads see coherent data by checking dirty mmap pages, pending writes, and dirty buffers; it may start a write section, upgrade the vnode lock, clean vnode pages, wait for buffer output, and call `ffs_syncvnode()`.
- `ffs_rawread_readahead()` builds a physical BIO read directly into mapped user pages using `vmapbuf()`, `ufs_bmaparray()`, and device vnode strategy; holes are filled with zeroes to preserve file semantics.
- `ffs_rawread_main()` drives the raw-read loop with one active pbuf and optional one-buffer readahead, waits for I/O completion, unmaps buffers, advances the `uio`, handles short reads/EOF/errors, and releases pbuf vnode references.
- `ffs_rawread()` decides whether the fast path can be used: raw reads must be enabled, single-iovec, userspace, full-resid read, not in deadlock-treatment mode, and sector-aligned by offset and length.
- Reads extending into a partial final filesystem block use raw I/O only for the full-block portion, leaving the remaining partial EOF handling to the normal buffered path.

Important patterns:
- The fast path prioritizes coherence before bypassing cache: dirty mmap and dirty buffers are flushed first.
- Physical mapping uses filesystem block mapping but avoids populating ordinary file buffers for the data transfer.
- Sparse holes are explicitly zero-filled rather than treated as I/O errors.
- Readahead is opportunistic and falls back cleanly if allocation or mapping setup fails.

Research relevance:
- Shows a FreeBSD FFS direct/raw read optimization distinct from ordinary `IO_DIRECT`.
- Useful for studying cache bypass constraints, vnode write-suspension interaction, dirty-page synchronization, and pbuf-based device I/O into user pages.
