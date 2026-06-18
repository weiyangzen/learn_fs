# File Research: sources/os/linux/linux/mm/readahead.c

## Purpose

`mm/readahead.c` implements page-cache readahead: proactively reading file data into the page cache before explicit demand. It handles synchronous cache-miss readahead, asynchronous follow-up readahead triggered by the readahead folio flag, forced readahead for `FMODE_RANDOM` or disabled window cases, large-folio readahead, and the `readahead(2)` syscall via `POSIX_FADV_WILLNEED`.

## Readahead Model

`struct file_ra_state` tracks:

- `start`: beginning page index of the last readahead window.
- `size`: total pages in the window.
- `async_size`: trailing async portion.
- `ra_pages`: maximum normal window.
- `prev_pos`: previous read position for sequential detection.
- `order`: preferred large-folio order.

The first folio in the async tail is marked with `PG_readahead`; when accessed, it triggers the next async readahead. This supports pipelined sequential reads and interleaved readers on the same file descriptor.

## Core I/O Submission

`read_pages()` drains prepared folios from a `readahead_control` and submits them through the mapping's address-space operations:

- Prefer `a_ops->readahead(rac)`.
- Fall back to repeated `a_ops->read_folio(file, folio)`.
- Remove and unlock any folios ignored by a filesystem `->readahead()`.
- Wraps submission in a block plug.
- Enters/leaves PSI memstall tracking if workingset folios are involved.

## Unbounded and Bounded Readahead

`page_cache_ra_unbounded()` prepares locked folios starting at `ractl->_index`, without clamping to `i_size`. It is intended for filesystem callers that know they may read beyond nominal size. It:

- Requires `mapping->invalidate_lock` held at least shared.
- Aligns indexes to mapping minimum folio size.
- Allocates folios with `readahead_gfp_mask()`.
- Adds folios to the xarray page cache.
- Marks the async trigger folio.
- Starts I/O through `read_pages()`.
- Uses `memalloc_nofs_save()` to avoid filesystem reclaim recursion.

`do_page_cache_ra()` is the normal bounded wrapper: it clamps reads to the file's current `i_size`, takes `filemap_invalidate_lock_shared()`, calls unbounded readahead, then unlocks.

`force_page_cache_ra()` reads a requested number of pages in chunks up to 2 MiB, capped by the larger of `bdi->io_pages` and `ra->ra_pages`.

## Window Sizing

`get_init_ra_size()` chooses an initial window by rounding to a power of two and scaling small/medium reads aggressively. `get_next_ra_size()` grows existing windows by 4x, 2x, or to max depending on current size.

`ractl_max_pages()` normally uses `ra->ra_pages`, but permits larger reads up to the device optimal I/O size when the request itself exceeds the normal window.

## Synchronous Readahead

`page_cache_sync_ra()` handles demand misses:

- If readahead is disabled or the block cgroup is congested, it may force a one-page read for the faulting request.
- `FMODE_RANDOM` forces direct requested-range readahead.
- Start-of-file, oversized, and sequential misses initialize a new window.
- Otherwise it probes prior page-cache misses with `page_cache_prev_miss()` to infer sequential history.
- Small standalone random reads read only the requested pages without polluting readahead state.
- The final read path uses `page_cache_ra_order()` to support large folios.

## Asynchronous Readahead

`page_cache_async_ra()` handles access to a marked readahead folio:

- Ignores disabled readahead, writeback folios, and congested blkcg.
- Clears the readahead flag.
- If the index matches expected state, advances and grows the window.
- Otherwise, probes for the next cache miss to recover from interleaved reads.
- Increases `ra->order` and aligns the window end for large-folio allocation.
- Makes the whole new window async.

## Large-Folio Readahead

`page_cache_ra_order()` allocates folios at `ra->order` when the mapping supports large folios. It clamps order by mapping maximum, current window size, and mapping minimum order, aligns indexes, avoids EOF overrun, and falls back to base readahead if allocation or page-cache insertion hits existing folios or errors.

`ra_alloc_folio()` allocates a folio, marks it if it contains the async trigger index, inserts it into the mapping, and updates the readahead control.

## Syscall and Expansion

`ksys_readahead()` validates the fd, read mode, mapping/aops, regular or block inode type, and rejects anonymous files. It delegates to `vfs_fadvise(..., POSIX_FADV_WILLNEED)`. Native and compat syscall wrappers expose this as `readahead(2)`.

`readahead_expand()` lets a filesystem expand an existing readahead request before and after the current window, inserting locked folios until it hits an existing folio or allocation/insertion failure. It updates the readahead state when trailing expansion succeeds.

## Filesystem/MM Relevance

This file is central to filesystem read performance. Filesystems implement `->readahead()` and consume prepared folios with `readahead_folio()`. The code defines when filesystems see synchronous versus async folios, how congestion and large folios affect read sizes, and how page-cache insertion is coordinated with `invalidate_lock`.
