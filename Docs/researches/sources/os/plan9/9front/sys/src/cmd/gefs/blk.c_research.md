# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/blk.c

## Purpose
Implements GEFS block allocation, block I/O, allocation logs, deferred frees, epochs, and sync queues.

## Key Elements
Provides atomic block flags, finalization and hashing, full-block reads/writes, arena selection, free-range AVL insertion/removal/coalescing, allocation-log append/load/flush/compression, block allocation/deallocation, new/duplicate block creation, cache-backed `getblk`, reference hold/drop, block-fill measurement, limbo/deferred free handling, epoch start/end/wait/clean, dirty-block enqueue, priority sync queue heap operations, and the sync worker loop.

## Dependencies
Uses Plan 9 file I/O, atomics, `QLock`/`Rendez`, AVL trees, global `fs` state, GEFS block types and packing/hash helpers from `dat.h`/`fns.h`, and the cache layer in `cache.c`.

## Behavior/Risks
Allocation logging is central to crash recovery and must avoid recursion while appending log blocks. Deferred frees are epoch-protected so old readers can finish before reuse. Sync queue ordering by generation/op/address preserves write/free/fence ordering. Any checksum mismatch marks corruption; sync errors push the filesystem read-only.
