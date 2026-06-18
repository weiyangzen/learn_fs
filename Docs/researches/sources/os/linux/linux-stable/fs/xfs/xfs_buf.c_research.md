# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf.c

## Purpose

Implements the XFS metadata buffer cache: buffer allocation, lookup, locking, I/O submission, verification, lifetime management, LRU reclaim, buffer targets, delayed-write queues, and magic-value helpers.

## Main Responsibilities

- Allocates and frees `struct xfs_buf` objects and backing memory.
- Caches buffers in a per-target rhashtable keyed by disk address and length.
- Manages buffer references with `lockref` and LRU references.
- Provides cached and uncached read/get paths.
- Handles synchronous and asynchronous metadata I/O.
- Runs read/write verifiers.
- Handles write I/O retry, permanent failure, and shutdown behavior.
- Implements buftarg shrinker/drain/destruction.
- Supports delayed-write queueing and submission.
- Configures block-device buffer targets.
- Verifies 16-bit and 32-bit metadata magic values.

## Buffer Backing Memory

The allocator uses:
- kmalloc for small power-of-two buffers
- single folio allocation when practical
- vmalloc fallback for large or irregular sizes
- tmpfs-backed memory mapping for in-memory buffer targets

Non-read buffers are zeroed at allocation.

## Lookup and Lifetime

`xfs_buf_get_map` verifies alignment/range, looks up buffers under RCU, locks cache hits, inserts misses, and handles stale buffers. New cached buffers hold a perag reference until destruction. Stale buffers are removed from the LRU and made immediately reclaimable.

## I/O Flow

- Reads set `XBF_READ`, submit bios, wait if synchronous, and run read verifiers.
- Writes set `XBF_WRITE`, wait for unpin, run write verifiers, and submit bios.
- Async I/O completion is moved to the XFS buffer workqueue.
- Multi-map buffers are submitted by splitting/chaining bios.
- In-memory targets complete without block I/O.

## Error Handling

Write I/O errors:
- are retried for async writes according to XFS error configuration
- mark log items failed for retryable async failures
- force shutdown on permanent metadata write failure
- stale buffers when completion cannot safely use their contents

Read errors clear `XBF_DONE`, stale the buffer, report I/O errors unless the log is already shut down, and translate bad CRC to metadata corruption.

## Delayed Write

Delayed-write lists:
- hold an extra buffer reference
- mark buffers with `_XBF_DELWRI_Q`
- can be cancelled
- can be submitted asynchronously while skipping locked or pinned buffers
- can be submitted synchronously with wait/error collection
- are sorted by disk address before submission

## Buftarg Management

A buftarg owns:
- block device and DAX references
- metadata/logical sector geometry
- buffer hash table
- LRU/shrinker state
- readahead counter
- I/O error ratelimit state
- atomic write unit geometry

Drain waits for readahead and completion work, reclaims LRU buffers, and reports permanent write-failure buffers.

## Important Invariants

- Buffer locks are semaphores; a newly allocated buffer starts locked and held.
- Stale pinned buffers can force the log before lock wait to avoid AIL stalls.
- Cached buffers must be sector aligned and within target bounds.
- `XBF_DONE` means buffer contents passed read verification or completed successful write.
- Async submission transfers lock/reference ownership to I/O completion.
- Delayed-write lists are caller-synchronized and must be emptied, retried, or cancelled.

## Dependencies

- Linux bio, rhashtable, list_lru, shrinker, lockref, folio/vmalloc APIs.
- XFS log, transaction, buf item, error injection, perag, memory-buf, and failure notification infrastructure.

## Research Notes

This is one of the core XFS metadata cache files. The most important design points are stale-buffer lifetime rules, log-pinned write synchronization, verifier attachment/reverification, and async write error retry semantics.
