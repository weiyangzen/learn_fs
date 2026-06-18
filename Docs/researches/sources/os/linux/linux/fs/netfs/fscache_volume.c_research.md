# File Research: sources/os/linux/linux/fs/netfs/fscache_volume.c

Implements FS-Cache volume cookie lifecycle management.

Key responsibilities:
- Allocates volume objects and hashes them by cache plus volume key.
- Pins cache access at volume granularity.
- Creates backend volume representation asynchronously.
- Handles hash collisions with relinquished volumes.
- Frees backend volume state and proc list entries.
- Exposes `/proc/fs/netfs/volumes`.

Important exported APIs:
- `__fscache_acquire_volume()`.
- `__fscache_relinquish_volume()`.
- `fscache_try_get_volume()`.
- `fscache_put_volume()`.
- `fscache_end_volume_access()`.
- `fscache_withdraw_volume()`.

Concurrency model:
- Hash buckets use `hlist_bl_lock`.
- Global add/remove and proc listing use `fscache_addremove_sem`.
- Volume creation uses `FSCACHE_VOLUME_CREATING` bit and workqueue.
- Access pins use `volume->n_accesses` and waiters sleep on the atomic variable.

Important behavior:
- Volume key is length-prefixed and padded before hashing.
- Collisions with already-relinquished volumes set pending flags and wait for the old volume to unhash.
- `fscache_create_volume()` pins the cache, schedules `acquire_volume`, and can optionally wait.
- `fscache_withdraw_volume()` decrements the artificial cache pin and waits until all volume accesses drain.

Dependencies:
- Cache lookup/refcounting from `fscache-cache.c`.
- Backend cache ops: `acquire_volume`, `free_volume`.
