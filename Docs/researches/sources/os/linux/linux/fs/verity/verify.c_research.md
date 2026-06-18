# File Research: sources/os/linux/linux/fs/verity/verify.c

## Purpose
Implements fs-verity data verification for reads, including Merkle tree traversal, hash block verification caching, bio/folio helpers, Merkle readahead, and the async verification workqueue.

## Main Functions
- Readahead:
  - `fsverity_readahead()`: starts readahead for Merkle tree pages needed to verify a data page range.
- Hash block cache:
  - `is_hash_block_verified()`: checks whether a hash block was already verified, using `PG_checked` when block size equals page size or a bitmap plus `PG_checked` generation marker otherwise.
- Verification:
  - `verify_data_block()`: verifies one data block by ascending the Merkle tree to root or an already-verified hash block, then descending and verifying each saved block.
  - `fsverity_init_verification_context()`: initializes pending block batching and enables two-block SHA-256 optimized hashing when available.
  - `fsverity_add_data_blocks()`: maps aligned data blocks from a locked non-uptodate folio into pending queue.
  - `fsverity_verify_pending_blocks()`: hashes pending data blocks and verifies them against the tree.
  - `fsverity_verify_blocks()`: public folio verification helper.
  - `fsverity_verify_bio()`: block-layer bio verification helper under `CONFIG_BLOCK`.
- Workqueue:
  - `fsverity_enqueue_verify_work()`: queues async verification work.
  - `fsverity_init_workqueue()`: creates high-priority per-CPU workqueue.

## Important Design Points
- Verification can stop ascending early when it hits a previously verified hash block, then descends to verify the path below it.
- Hash pages evicted and reloaded must be reverified; `PG_checked` is used as a new-page marker even when a separate bitmap tracks sub-page hash blocks.
- Memory barriers pair with `PG_checked` to ensure bitmap clearing is visible before later checked reads.
- Data blocks wholly beyond EOF must be zero-filled, because mmap can expose page portions past EOF when Merkle block size is smaller than page size.
- Supports optimized two-block SHA-256 finup when available.
- Corruption logs include position, level, expected hash, and actual hash.
- Async workqueue is high priority and per-CPU, avoiding unbound crypto work due to scheduler latency concerns.

## Cross-File Relationships
- Uses tree params and cached info from `open.c`.
- Calls filesystem `read_merkle_tree_page()` and optional `readahead_merkle_tree()`.
- Exported helpers are called by filesystems from read-folio/readahead/bio completion paths.

## Risks / Review Notes
- Callers must pass locked, not-yet-uptodate folios with length/offset aligned to Merkle block size.
- All mapped pages must be unmapped/released on failure paths; the code has explicit cleanup loops.
- Verification cache correctness depends on `PG_checked` and bitmap memory ordering.
- A failed verification sets bio status to `BLK_STS_IOERR` or returns false for folio callers; filesystems must propagate that correctly.
