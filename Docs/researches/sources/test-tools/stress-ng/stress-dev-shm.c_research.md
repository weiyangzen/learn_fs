# sources/test-tools/stress-ng/stress-dev-shm.c

## Purpose
This Linux-only stressor exercises `/dev/shm` by creating an unlinked shared-memory-backed file, expanding it with `fallocate()`, mapping it, touching and verifying pages, applying random madvise behavior, and reporting mmap residency/dirty/swap statistics.

## Important APIs, Types, And Functions
`stress_dev_shm_context_t` stores the `/dev/shm` file descriptor and accumulated `stress_mmap_stats_t`. `stress_dev_shm_child()` performs truncate, rough maximum-size probing, mmap, page touch, verification, msync invalidation, and unmap work under an OOMable child. `stress_dev_shm()` validates `/dev/shm`, creates and unlinks the backing file, runs the child through `stress_oomable_child()`, reports mmap stats, closes the fd, and unmaps context.

## Control Flow
The top-level stressor maps a shared context, checks `/dev/shm` read/write availability, opens a unique file with `O_CREAT|O_EXCL|O_RDWR`, unlinks it, synchronizes, and starts an OOMable child. The child truncates the file to zero, uses an exponential/rough binary search with `shim_fallocate()` to find a large size, maps it private read/write, collects mapping stats, names and advises the mapping, writes one word per page using an address-derived value, verifies the same values, invalidates with `msync()`, unmaps, truncates to zero, and repeats.

## State And Persistence
The backing file is unlinked immediately, so storage pressure is transient and tied to the open fd. Shared context persists only for the worker lifetime. Reported state includes total, swapped, and dirtied mmap statistics accumulated from child observations.

## Dependencies And Integration Points
This file depends on Linux `/dev/shm`, stress-ng OOM child handling, madvise helpers, mmap stats helpers, random generators, file allocation/truncation shims, and stress-ng process state/metrics. Non-Linux builds register an unimplemented stressor.

## Risks
The workload can fill tmpfs and trigger `SIGBUS` or OOM pressure; the search deliberately avoids exact maximum sizing to reduce that risk. Private mappings mean writes fault private pages and may stress memory more than tmpfs persistence. Verification is page-stride based, not byte-for-byte. Cleanup must close the unlinked fd and unmap shared context on all paths.

## Test Signals
Signals include skip behavior when `/dev/shm` is missing or inaccessible, successful repeated allocation/map/verify cycles, no leaked named files, mmap stats output, and graceful OOM/no-resource behavior under small tmpfs limits.
