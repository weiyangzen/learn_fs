# File Research: sources/os/linux/linux-stable/fs/iomap/buffered-io.c

This file implements iomap buffered I/O over folios: buffered reads, readahead, buffered writes, dirty tracking, invalidation, delayed-allocation release, zeroing, page-mkwrite, and writeback.

Key responsibilities:
- Defines `struct iomap_folio_state`, which tracks per-block uptodate and dirty bits plus pending read/write byte counts for folios larger than filesystem blocks.
- Provides helpers to allocate/free folio private state, mark ranges uptodate or dirty, locate dirty/clean/uptodate ranges, and clear dirty subranges.
- Adjusts read ranges to skip already-uptodate blocks and avoid reading beyond EOF.
- Handles inline data reads through `iomap_read_inline_data()`.
- Completes reads via `iomap_finish_folio_read()`, including filesystem error reporting and per-folio pending-byte accounting.
- Implements `iomap_read_folio()` and `iomap_readahead()` using `iomap_iter` plus pluggable read operations.
- Provides partial-uptodate checks for filesystems with sub-folio block state.
- Implements buffered write begin/end paths, including stale iomap validation, optional buffer-head fallback, inline write handling, short-copy retry behavior, folio sizing, and page-cache size extension.
- Exports `iomap_file_buffered_write()` as the generic buffered write implementation.
- Provides delayed-allocation cleanup in `iomap_write_delalloc_release()`, preserving dirty cached ranges while punching unused delalloc reservations.
- Implements unshare, zero-range, truncate-page zeroing, and page-mkwrite support.
- Implements writeback helpers: per-folio writeback initialization, completion, dirty-range iteration, EOF handling, and `iomap_writepages()`.

Important interactions:
- Uses iomap iteration callbacks from filesystems to translate logical file ranges into mapping state.
- Calls BIO-backed read helpers from `bio.c` for synchronous or asynchronous reads when custom write/read ops are absent.
- Coordinates with page cache APIs, folio locking, writeback iteration, dirty throttling, invalidate locks, and filesystem error reporting.
- Supports both pure iomap folio state and buffer-head compatibility via `IOMAP_F_BUFFER_HEAD`.

Notable invariants and risks:
- Per-block dirty and uptodate state is mandatory for correctness when filesystem block size is smaller than folio size.
- Read completion must avoid marking the whole folio uptodate while asynchronous read bytes are still pending.
- Delalloc release requires the caller to hold `mapping->invalidate_lock` for write to prevent page faults from dirtying folios after reservation punching.
- Write begin must revalidate stale mappings to avoid data corruption after concurrent extent conversion or reclaim.
- EOF writeback handling must avoid repeatedly writing folios entirely beyond `i_size`, including large offsets on 32-bit systems.
- Writeback from reclaim context is refused with a warning because iomap writeback should not run from direct reclaim.

Research notes:
- This is the core buffered-I/O engine for iomap-based filesystems. Its main complexity is maintaining byte/block-level correctness across large folios, delayed allocation, mmap faults, writeback, EOF, and concurrent extent-state changes.
