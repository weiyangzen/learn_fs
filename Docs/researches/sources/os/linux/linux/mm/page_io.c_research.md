# File Research: sources/os/linux/linux/mm/page_io.c

Swap I/O implementation for writing swapcache folios to backing storage and reading them back. It covers swapfile activation extent discovery, zero-page swap optimization, zswap integration, block-device swap I/O, and filesystem-provided swap I/O.

Key responsibilities:
- Implements generic swapfile activation by walking file blocks with `bmap()`, requiring page-sized contiguous disk runs and building swap extents.
- Handles swap write completion and read completion for block-device BIO paths.
- Detects zero-filled folios on swapout, records entries in the swap `zeromap`, and avoids physical I/O for those pages.
- Clears stale zeromap bits when non-zero data is written to reused swap entries.
- Integrates zswap store/load and memcg zswap writeback policy.
- Provides write paths for filesystem swap operations (`swap_rw` with `swap_iocb` batching), synchronous block I/O, and asynchronous BIO block I/O.
- Provides read paths for filesystem swap operations, synchronous BIO, asynchronous BIO, zeromap reads, and zswap loads.
- Maintains swap-in/swap-out VM, memcg, THP, and multi-size THP statistics.

Important behavior:
- `swap_writeout()` first frees stale swapcache entries if possible, then lets architecture code preserve metadata via `arch_prepare_to_swap()`.
- Zero-filled folios are counted and unlocked without I/O; swapin reconstructs them by zeroing the folio and marking it uptodate.
- Filesystem swap I/O batches adjacent folios into a mempool-allocated `swap_iocb`; unplug submits through `mapping->a_ops->swap_rw()`.
- Block-device synchronous swap I/O waits with a stack BIO; asynchronous I/O owns a heap BIO and completion callback.
- Swap read accounting includes PSI/delayacct stall tracking for workingset refaults.
- Read/write errors unlock or end writeback safely and leave failed write folios dirty/reclaimable enough to avoid data loss.

Dependencies:
- Uses swap metadata, swap extents, `swap_info_struct`, folios, BIO/block layer APIs, writeback, zswap, memcg, blk-cgroup association, PSI, delay accounting, object cgroup counters, and filesystem `swap_rw` address-space operations.

Notable risks:
- Folios must enter write paths locked and in swapcache; write paths must unlock or start/end writeback in exactly the right branch.
- Zeromap correctness depends on locked swapcache folios and atomic bitmap updates, especially when swap entries are reused.
- Large folio swapin from partially zeromapped batches is intentionally not handled and is warned/error-directed.
- Filesystem batching must preserve contiguous file offsets and matching swap files before extending a plug.
