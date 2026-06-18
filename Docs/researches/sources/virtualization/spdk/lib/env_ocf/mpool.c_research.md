# File Research: sources/virtualization/spdk/lib/env_ocf/mpool.c

Implements OCF-style multi-size memory pools using SPDK-backed `env_allocator` objects.

Important behavior:
- `env_mpool_create()` creates allocators for powers-of-two item counts from 1 through the configured max order.
- Each pool element size is `hdr_size + elem_size * (1 << i)`.
- Optional per-pool limits and zeroing are passed through to `env_allocator_create_extended()`.
- `env_mpool_get_allocator()` rounds requested count up to the appropriate power-of-two allocator.
- `env_mpool_new()` allocates from the matching allocator or falls back to `env_vmalloc()` when enabled.
- `env_mpool_del()` returns objects to the matching allocator or frees fallback allocations.

Risk note: deallocation requires the same `count` classification used at allocation time; otherwise the object may be returned to the wrong backing pool.
