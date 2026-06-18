# File Research: sources/os/linux/linux/mm/list_lru.c

Generic kernel LRU-list infrastructure for shrinkers, with optional per-memcg/per-NUMA accounting and reparenting support.

Key responsibilities:
- Provides exported operations to add, delete, isolate, move, count, walk, initialize, and destroy `struct list_lru`.
- Maintains one `list_lru_one` per NUMA node for non-memcg LRUs.
- Under `CONFIG_MEMCG`, maintains xarray-indexed per-memcg/per-node `list_lru_memcg` instances.
- Registers memcg-aware LRUs on a global `memcg_list_lrus` list so dying cgroups can reparent all associated LRUs.
- Integrates list activity with shrinker bits through `set_shrinker_bit()`.

Important behavior:
- `list_lru_add()` inserts only if the item list head is empty, increments local and node-wide counts, and sets the shrinker bit when a list transitions from empty.
- `list_lru_del()` removes only if the item is linked and decrements both local and node-wide counts.
- `list_lru_add_obj()` and `list_lru_del_obj()` derive the NUMA node and, when memcg-aware, the memcg from the object address.
- `__list_lru_walk_one()` walks a locked LRU and delegates isolation decisions to a callback returning `LRU_REMOVED`, `LRU_REMOVED_RETRY`, `LRU_ROTATE`, `LRU_SKIP`, `LRU_RETRY`, or `LRU_STOP`.
- `list_lru_walk_node()` first walks the root list for the node, then iterates memcg xarray entries when the LRU is memcg-aware.
- Memcg reparenting moves each dying cgroup's per-node lists into the parent, marks the source `nr_items` as `LONG_MIN`, erases the xarray slot, and frees the memcg LRU after RCU grace.
- `memcg_list_lru_alloc()` ensures a memcg and all not-yet-populated ancestors have list-LRU storage before use.
- `__list_lru_init()` allocates per-node storage, records the shrinker id, disables memcg awareness if kmem accounting is off, initializes locks/lists, and registers the LRU.
- `list_lru_destroy()` unregisters, frees all memcg xarray entries, releases node storage, and resets the shrinker id.

Dependencies:
- Uses `struct list_lru`, `list_lru_node`, `list_lru_one`, and callback semantics from `linux/list_lru.h`.
- Depends on memcg APIs, xarray, RCU, shrinker ids, NUMA node iteration, spin locks, and slab allocation helpers.
- Uses lockdep class assignment when a list LRU provides a lock class key.

Notable risks:
- Callers must ensure memcg lifetime for direct `list_lru_add()`/`list_lru_del()` calls.
- Reparenting races are handled by marking source lists with `LONG_MIN`; code that ignores this sentinel could corrupt lists or counts.
- Walk callbacks may drop the LRU lock for retry states, so traversal restarts and callback contracts must be respected.
- `list_lru_count_one()` clamps negative counts to zero because reparented/dead lists use a negative sentinel.
- Memcg allocation is ancestor-aware and can return xarray allocation errors; callers must be prepared for allocation failure.
