# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/buf.c

Implements the asynchronous buffer cache for `hjfs`.

Key points:
- Maintains free buffers, device hash lists, per-buffer wait queues, and global pending free-buffer requests.
- `markbusy()` removes a buffer from the free list; `markfree()` returns it.
- `changedev()` moves a buffer between device/off hash chains.
- `givebuf()` satisfies get requests from cached buffers, waits on busy buffers, or recycles free buffers.
- Delayed-write buffers are scheduled for writeback before reuse.
- `handleput()` handles immediate writeback (`BWRIM`), delayed write errors, freeing, and waking waiters.
- `handlesync()` schedules all delayed-write buffers and can notify a waiting caller.
- `bufproc()` multiplexes get, put, and sync channels, and starts 9P workers.
- Installs `%T` formatting for block types.
- `bufinit()` allocates buffers with `sbrk`, initializes channels, and starts `bufproc`.
- `getbuf()` checks bounds, fetches or allocates a buffer, validates expected block type, and records caller pc for debugging.
- `sync(wait)` flushes delayed writes and optionally sends sync sentinel work to every device.

Dependencies and interactions:
- Device I/O is performed by `dev.c` workers through per-device work queues.
- Used by almost every filesystem operation to access superblocks, dentries, indirect blocks, raw data, and ref blocks.

Research relevance:
- Central cache/writeback layer for `hjfs`, mediating concurrency, type checking, delayed writes, and sync.
