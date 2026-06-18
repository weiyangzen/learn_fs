# File Research: sources/os/linux/linux-stable/fs/verity/verify.c

Implements fs-verity read-time data verification. `fsverity_readahead()` walks Merkle tree levels for an upcoming data page range and asks the filesystem to readahead needed hash pages.

The core verifier is `verify_data_block()`. It hashes a data block, ascends the Merkle tree loading hash pages until it finds an already verified hash block or reaches the root, then descends and verifies each hash block against the expected digest before checking the data block digest. Verified hash blocks are cached using `PG_checked` when block size equals page size, or an in-memory bitmap plus `PG_checked` page freshness tracking when they differ. It also verifies fully past-EOF blocks are zeroed.

`fsverity_verify_blocks()` verifies aligned data in a locked, not-yet-uptodate folio. `fsverity_verify_bio()` does the same for completed read bios and marks `bi_status` on failure. The verification context can batch two SHA-256 blocks when optimized 2x hashing is available. The file also creates a high-priority per-CPU workqueue used by asynchronous verification work.
