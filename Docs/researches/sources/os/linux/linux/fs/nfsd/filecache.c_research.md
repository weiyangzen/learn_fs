# File Research: sources/os/linux/linux/fs/nfsd/filecache.c

Read completely: 1430 lines.

NFSD open-file cache implementation. It caches `struct file` instances by inode, credential, network namespace, access mode, and garbage-collection policy, while coordinating delayed close, writeback-error detection, localio acquisition, fsnotify invalidation, lease conflicts, shrinker reclaim, and statistics.

Key responsibilities:
- Maintains a global rhashtable keyed by inode pointer and a list_lru for garbage-collected entries.
- Allocates `struct nfsd_file` entries with current credentials, net namespace, access mask, pending construction state, optional GC mode, and direct-I/O alignment fields.
- Provides safe refcount operations (`nfsd_file_get`, `nfsd_file_put`, `nfsd_file_put_local`) and RCU-delayed slab freeing.
- Uses `NFSD_FILE_PENDING` plus `wait_on_bit()` to let concurrent acquirers wait for one thread to finish opening and hashing a file.
- Opens verified files through `nfsd_open_verified` or adopts an already-open file, records DIO alignment via `fh_getattr`, retries stale opens once, and breaks leases before returning cached entries.
- Keeps GC entries on an LRU; the laundrette ages recent entries, the shrinker reclaims under memory pressure, and close work is batched through per-net disposal lists.
- Invalidates cached opens on fsnotify `FS_ATTRIB`/`FS_DELETE_SELF`, lease notifications, export flush, net shutdown, and synchronous rename/unlink paths.
- Resets the write verifier if a cached writable file observes a new writeback error.
- Registers and unregisters slab caches, list_lru, shrinker, fsnotify group, lease notifier, delayed work, and per-net disposal queues.
- Reports filecache stats through `nfsd_file_cache_stats_show`.

Important interactions:
- Uses `nfsd_mutex` for global cache startup/shutdown and purge synchronization.
- Uses `nfsd_net.fcache_disposal` to defer expensive file closes to nfsd service threads.
- LOCALIO calls `nfsd_file_acquire_local`, which verifies filehandle access using supplied service credentials instead of a live RPC request.
- Export flush calls into the file cache to close files that may retain stale export state.

Notable risks:
- `nf_inode` intentionally does not hold an inode reference and must be used only for lookup comparison.
- Refcount and LRU accounting are tightly coupled; GC entries hold an extra LRU reference that must be removed before final free.
- Shutdown ordering is sensitive: delayed work, shrinker callbacks, fsnotify marks, RCU freeing, and per-net disposal queues all have to drain before slab/table destruction.
- LOCALIO is explicitly security-sensitive because it allows a kernel client to bypass normal network request authorization using mapped credentials.
