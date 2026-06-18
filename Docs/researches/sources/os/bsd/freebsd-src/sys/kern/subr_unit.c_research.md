# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_unit.c

## Purpose
Implements compact unit-number allocation (`unrhdr`) with lowest-free-number-first policy. It is used by kernel subsystems that need integer IDs, minor/unit numbers, or similar finite/infinite-ish number spaces.

## Representation
- `struct unrhdr` tracks low/high bounds, compact leading allocated run (`first`), trailing free run (`last`), busy count, allocated chunk count, active chunk list, postponed-free list, and optional mutex.
- `struct unr` is the basic chunk:
  - `ptr == NULL`: free run,
  - `ptr == uh`: allocated run,
  - other pointer: bitmap (`struct unrb`) representing mixed allocation.
- `NBITS` is the number of allocatable bits stored in a bitmap the size of `struct unr`.

## Locking and Allocation Constraints
- If no mutex is supplied, a global `unitmtx` is used.
- `UNR_NO_MTX` disables locking.
- `alloc_unrl()` requires the mutex already held and never sleeps.
- `alloc_unr()` locks, allocates, cleans postponed frees, and unlocks.
- `free_unr()` may allocate memory and may sleep; it preallocates two chunks before locking.
- `clean_unrhdrl()` frees postponed chunks while temporarily dropping the allocator mutex.

## Lifecycle
- `init_unrhdr()` initializes an existing header.
- `new_unrhdr()` allocates and initializes a header.
- `delete_unrhdr()` asserts no busy allocations, no memory leak, and no postponed frees.
- `clear_unrhdr()` frees all chunks and reinitializes the range.

## Allocation
- `alloc_unrl()` returns the lowest free number:
  - ideal compact case uses only `first`/`last`;
  - otherwise consumes from the first chunk, either shrinking a free run or setting the first clear bitmap bit;
  - then calls `collapse_unr()` to simplify representation.
- `alloc_unr_specific()` preallocates memory and calls `alloc_unr_specificl()` to allocate a requested item.
- `alloc_unr_specificl()` rejects out-of-range or already allocated items, creates/splits chunks as needed, updates `last`, increments busy count, and collapses/optimizes.

## Freeing
- `free_unr()` preallocates chunks, locks, calls `free_unrl()`, cleans postponed frees, unlocks, and frees unused preallocations.
- `free_unrl()` validates range and that the item is allocated, then:
  - adjusts compact ideal/leading regions,
  - clears bitmap bits,
  - converts single allocated runs to free runs,
  - shifts boundary frees into neighboring free runs,
  - or splits an allocated run around the freed item.
- `collapse_unr()` converts full/empty bitmaps to runs, deletes zero-length chunks, merges adjacent same-kind runs, folds leading allocated/trailing free runs into `first`/`last`, and calls `optimize_unr()`.

## Compaction
- `optimize_unr()` finds adjacent chunks that can fit into one bitmap and saves memory by combining runs/bitmaps into bitmap representation.
- Bitmap conversion uses postponed frees via `delete_unr()` so memory can be freed safely later.

## Iteration and Debugging
- `create_iter_unr()`, `next_iter_unr()`, and `free_iter_unr()` iterate allocated unit numbers in increasing order.
- Diagnostic `check_unrhdr()` verifies busy count and chunk allocation count.
- DDB/userland debug helpers print allocator headers, runs, and bitmaps.
- DDB commands can show `unrhdr` and iterator state.

## Userland Test Driver
When not built in `_KERNEL`, the file includes:
- libc/pthread-free shims for mutex/allocation assertions,
- stochastic allocation/free tests,
- iterator tests,
- command-line options for repetitions, iterator mode, and verbosity.

## Filesystem Relevance
Filesystems and storage drivers often need compact ID spaces for units, devices, clone IDs, request IDs, or minor numbers. This allocator provides a memory-efficient kernel primitive for those uses.
