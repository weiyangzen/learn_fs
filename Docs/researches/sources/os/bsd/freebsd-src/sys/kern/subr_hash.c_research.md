# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_hash.c

## Purpose
Provides generic hash table allocation and teardown helpers for multiple queue-head types and optional per-bucket lock types.

## Key Elements
- Core allocator: `hashalloc()`.
- Core free path: `hashfree()`.
- Compatibility helpers: `hashinit_flags()`, `hashinit()`, `hashdestroy()`.
- Prime-size helpers: `phashinit_flags()`, `phashinit()`.
- Shape calculator: `hashalloc_sizes()`.
- Static padding assertions for queue-head plus lock layouts.

## Behavior
`hashalloc()` chooses either a power-of-two bucket count or a prime count from a fixed table. It computes each bucket header size from requested queue head and lock type, honors caller-provided `hdrsize`, allocates the table, initializes each queue head, initializes requested locks, and optionally runs a caller constructor per bucket.

Supported heads include LIST, CK_LIST, SLIST, CK_SLIST, STAILQ, CK_STAILQ, and TAILQ. Supported locks include none, mutex, rwlock, sx, rmlock, and rmslock.

`hashfree()` optionally runs destructors, asserts buckets are empty under `INVARIANTS`, destroys per-bucket locks, and frees the backing memory. Legacy helpers build `struct hashalloc_args` for common power-of-two or prime hash tables.

## Research Notes
The file is infrastructure for many kernel hash tables. The `_Static_assert` checks are important because callers may rely on predictable head-plus-lock packing.
