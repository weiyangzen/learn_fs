# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpcache.c

Purpose: Provides the in-memory lump cache keyed by score and block type.

Key behavior:
- `initlumpcache` allocates a fixed descriptor pool, hash table, victim heap, and byte budget.
- `lookuplump` finds or allocates a `Lump`, pins it with a refcount, updates two-generation usage timestamps, and locks the returned lump.
- `insertlump` attaches packet data to a lump while evicting victims until enough packet memory is available.
- `putlump` releases the lump lock, decrements the refcount, and returns unreferenced entries to the eviction heap.
- `bumplump` evicts the oldest eligible lump from the heap, removes it from the hash table, frees packet data, and returns the descriptor to the free list.
- Heap helpers maintain a victim heap ordered by second-most-recent use.

Dependencies:
- Uses Plan 9 `QLock`/`Rendez`, packet ownership, hash/score helpers, stats counters, and server tracing.

Notable details:
- The replacement policy uses the “second to last use” timestamp, approximating LRU with protection for recently reused entries.
- `CHECK(checklumpcache())` is compiled out by default but can validate heap, hash, free-list, refcount, and memory accounting invariants.
