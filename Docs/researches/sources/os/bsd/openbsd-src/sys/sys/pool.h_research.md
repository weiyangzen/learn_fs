# File Research: sources/os/bsd/openbsd-src/sys/sys/pool.h

Defines OpenBSD’s fixed-size item allocator and pool-cache statistics. Public/sysctl-visible structures report pool sizing, allocation counts, failures, page counts, idle pages, and per-CPU cache activity.

Kernel/libkvm content defines pool allocators, page-size capability encoding, `struct pool` with page lists, locks, object counts, hard limits, per-CPU caches, request queues, instrumentation, and physical memory constraints. Kernel APIs include pool init/destroy, low/high water settings, hard limits, constraints, get/put, async requests, wakeup, reclaim, prime, diagnostics, and DMA allocator wrappers.

This allocator backs many VFS/kernel objects including process, vnode-adjacent, and network allocations.
