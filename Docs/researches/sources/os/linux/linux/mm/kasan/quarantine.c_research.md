# File Research: sources/os/linux/linux/mm/kasan/quarantine.c

Generic KASAN quarantine implementation for delaying reuse of freed slab objects.

Data structures:
- `qlist_head`: singly linked queue with head, tail, byte count, and offline flag.
- Per-CPU `cpu_quarantine` queues.
- Global round-robin `global_quarantine[]` batch array protected by `quarantine_lock`.
- Per-CPU `shrink_qlist` staging queues.
- SRCU domain `remove_cache_srcu` for cache-removal synchronization.

Key behavior:
- `kasan_quarantine_put()` queues freed objects in per-CPU quarantine. When a per-CPU queue exceeds 1 MiB, it is moved to global quarantine and batched.
- `kasan_quarantine_reduce()` trims global quarantine when over its dynamic max, recalculating limits from total RAM and online CPUs.
- `kasan_quarantine_remove_cache()` removes and frees all quarantined objects belonging to a cache, coordinating per-CPU lists, global lists, and in-flight reduction with `on_each_cpu()` and SRCU.
- CPU hotplug callbacks mark per-CPU queues offline/online and free quarantined objects on offline.

Important details:
- `qlink_to_object()` reconstructs object address from KASAN free metadata offset.
- `qlink_free()` preserves metadata for UAF-before-realloc reports, but zeros in-object free metadata when `init_on_free` requires it.
- Quarantine is generic-KASAN-only; tag-based modes use stack rings and tag mismatch rather than delayed reuse.
