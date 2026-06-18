# File Research: sources/local-fs/xfsprogs/repair/prefetch.c

## Role

`prefetch.c` implements threaded inode and metadata read-ahead for repair phases. It primes the libxfs buffer cache with inode clusters, directory data, directory bmap btree blocks, and selected metadata so later phase processing blocks less on disk I/O.

## Core Behavior

- `init_prefetch()` records the mount, device fd, and batch sizing.
- `start_inode_prefetch()` creates per-AG prefetch state and a queueing worker, optionally chained after a previous AG.
- `pf_queuing_worker()` walks inode records in an AG, queues non-sparse inode clusters, starts I/O workers, and throttles read-ahead with a semaphore.
- `pf_io_worker()` drains queued buffers with batched `pread()` operations.
- `pf_read_inode_dirs()` verifies inode buffers and queues directory data or bmap btree blocks when useful.
- `do_inode_prefetch()` chooses between cache-only parallel processing, single-thread prefetch, or segmented threaded prefetch.
- `wait_for_inode_prefetch()` gates processing until enough data is queued or ready.
- `cleanup_inode_prefetch()` joins workers and destroys per-AG state.

## Queueing Strategy

Buffers are held in an AVL/btree keyed by fsblock. Primary and secondary queues avoid running too far ahead of processing. Directory metadata receives higher cache priority than generic inode buffers because later phases reuse it more often.

## Dependencies

This file uses pthreads, semaphores, libxfs buffers, bmap parsing, directory geometry, repair inode trees, workqueues, and progress/thread RCU registration.

## Risk Areas

- Prefetch intentionally ignores I/O errors; real repair logic must still validate buffers later.
- Buffer locks are acquired with trylock to avoid deadlocks with repair code.
- Aggressive prefetch can thrash the libxfs cache, so the chaining and semaphore limits are part of correctness for performance.
