# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_volume.c

Implements FS-Cache volume cookies, the parent objects under which data cookies live.

Key behavior:
- Allocates volume records tied to a named cache and volume key, with optional coherency data.
- Maintains a volume hash table and collision wait logic similar to data cookies.
- Uses `n_accesses` to pin volume/cache access while backend volume operations run.
- `fscache_create_volume()` schedules backend `acquire_volume()` work and can wait for completion.
- Relinquish records updated coherency data or invalidate intent, then drops the caller reference.
- Free path calls backend `free_volume()`, removes proc and hash links, decrements cache volume count, and drops cache reference.
- `fscache_withdraw_volume()` prevents new access by unpinning and waiting for active volume accesses to drain.
- Proc output lists volume refs, cookie counts, accesses, flags, cache name, and key.

Important interactions:
- Cookies hold volume references after successful hash insertion.
- Cookie lookup creates the backend volume on demand if needed.
