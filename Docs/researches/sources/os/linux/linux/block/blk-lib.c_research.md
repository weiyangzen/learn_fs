# File Research: sources/os/linux/linux/block/blk-lib.c

## Summary
Provides generic block-device helper functions for issuing discard, write-zeroes, explicit zero-page writes, zeroout, and secure erase operations as chains of bios.

## Main Responsibilities
- Split discard bios on granularity and maximum bio size constraints.
- Submit discard requests and normalize `-EOPNOTSUPP` for discard.
- Prefer hardware `WRITE ZEROES` for zeroout when available.
- Fall back to writing the shared zero folio unless disabled.
- Submit secure erase requests respecting device limits and alignment.

## Key APIs
- `blk_alloc_discard_bio()`.
- `__blkdev_issue_discard()`.
- `blkdev_issue_discard()`.
- `__blkdev_issue_zeroout()`.
- `blkdev_issue_zeroout()`.
- `blkdev_issue_secure_erase()`.

## Important Behavior
Discard splitting aligns subsequent bios to discard granularity and rounds sizes down when possible. Zeroout validates logical-block alignment and read-only state before issuing I/O.

`blkdev_issue_zeroout()` first tries `REQ_OP_WRITE_ZEROES` when the queue advertises support. If that path reports unsupported, it falls back to explicit zero-page writes unless `BLKDEV_ZERO_NOFALLBACK` was requested.

Killable zeroing checks `fatal_signal_pending(current)` in the loop and stops generating more bios. Long loops call `cond_resched()` to avoid soft lockups.

## State and Synchronization
The helpers use local bio chains and `blk_plug` batching. They do not own persistent state; behavior is driven by current block-device limits and flags.

## Risks
Several limits may change at runtime, especially write-zeroes support after SCSI errors. Callers must pass aligned sector ranges for zeroout and secure erase. Fallback zero-page writes can be much more expensive than hardware zeroing.
