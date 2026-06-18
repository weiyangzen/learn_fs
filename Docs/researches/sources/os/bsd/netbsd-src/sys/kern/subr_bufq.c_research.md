# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_bufq.c

## Summary
Implements the machine-independent buffer queue strategy registry and wrapper API used by disk/block drivers to allocate, operate, inspect, drain, move, and destroy `struct bufq_state` queues.

## Main Responsibilities
- Maintains the global `bufq_strat_list` protected by `bufq_mutex`.
- Registers and unregisters `struct bufq_strat` implementations, tracking per-strategy references.
- Selects a queue strategy by exact name or highest priority and can autoload `bufq_<strategy>` modules.
- Provides generic wrappers for queue put/get/peek/cancel/drain/free/move.
- Exposes `kern.bufq.strategies` sysctl output listing registered strategies.

## Important Behavior
`bufq_alloc()` normalizes sort flags, refuses impossible sort modes, autoloads missing named strategies unless the module generation did not change, and falls back to the best priority strategy unless `BUFQ_EXACT` requires `ENOENT`.

`bufq_free()` asserts the queue is empty, calls the strategy finalizer, decrements the strategy refcount, and frees the state. `bufq_drain()` completes all queued buffers with `EIO`.

## Dependencies
Uses `sys/bufq_impl.h` strategy hooks, `struct buf`, module autoloading, `kmem`, `sysctl_createv`, and `copyout` for sysctl string construction.

## Risks
Strategy unload safety depends on `bs_refcnt` being updated only through `bufq_alloc()`/`bufq_free()`. Sysctl output walks the strategy list without taking `bufq_mutex`, so it assumes registration churn is externally benign for this diagnostic path.
