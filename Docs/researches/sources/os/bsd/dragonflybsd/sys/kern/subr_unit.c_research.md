# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_unit.c

## Summary
Implements DragonFly BSD's compact unit-number allocator. It manages integer allocation ranges with a hybrid representation of leading allocated count, trailing free count, run-length list entries, and inline-sized bitmaps.

## Main Responsibilities
- Creates and destroys allocation spaces with `new_unrhdr()` and `delete_unrhdr()`.
- Allocates the lowest available unit via `alloc_unr()` and prelocked `alloc_unrl()`.
- Frees allocated units via `free_unr()` and internal `free_unrl()`.
- Converts fragmented run sequences into bitmap entries through `optimize_unr()`.
- Collapses empty, adjacent, fully allocated, and fully free entries through `collapse_unr()`.
- Provides diagnostic consistency checking and a userland stochastic test driver under `#ifndef _KERNEL`.

## Important Behavior
The allocator always returns the lowest free unit. The ideal case with only a prefix of allocated units and suffix of free units uses no list nodes. List entries represent free runs (`ptr == NULL`), allocated runs (`ptr == uh`), or bitmap chunks (`ptr` points to `struct unrb`). Bitmap storage is deliberately the same size as `struct unr`, allowing conversion without net extra memory in some cases.

`alloc_unrl()` requires the caller to hold the allocator lock and does not sleep. `free_unr()` may allocate two cached list nodes before taking the lock because freeing a unit can split an allocated run into several pieces.

## Dependencies and Integration
Kernel builds use `kmalloc`/`kfree`, `M_UNIT`, and a default global `unit_lock` unless the caller supplies a lock. Consumers are expected to use this for driver/device minor numbers, clone indexes, and other small kernel identifier spaces.

## Risks
The data structure has subtle invariants around `first`, `last`, `busy`, `alloc`, bitmap `busy`, and list length. Freeing an unallocated number or deleting a non-empty allocator triggers assertions. Correct prelocking is required for `alloc_unrl()`, while `free_unr()` must remain sleepable because it may need memory.
