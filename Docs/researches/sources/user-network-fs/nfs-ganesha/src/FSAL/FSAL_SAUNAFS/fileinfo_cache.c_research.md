# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.c

This file implements a small thread-safe cache for SaunaFS `sau_fileinfo_t` objects used mainly by pNFS data-server handles. It tracks entries by inode, separates in-use entries from LRU entries, and expires entries by timeout or maximum count pressure.

Private types are `struct FileInfoEntry` and `struct FileInfoCache`. Entries contain list/tree hooks, inode, `fileinfo`, timestamp, `is_used`, and a `lookup` flag used by the AVL comparator. The cache contains LRU and used lists, an AVL tree for available entries, count/limit settings, timeout, and a mutex. Public APIs are `createFileInfoCache`, `resetFileInfoCacheParameters`, `destroyFileInfoCache`, `acquireFileInfoCache`, `releaseFileInfoCache`, `eraseFileInfoCache`, `popExpiredFileInfoCache`, `fileInfoEntryFree`, `extractFileInfo`, and `attachFileInfo`.

Control flow: acquire looks up an unused entry by inode in the AVL tree; if found, it moves it from LRU to used and removes it from lookup, otherwise allocates a new entry. Release moves a used entry to LRU and reinserts into the AVL tree. Pop-expired inspects the oldest LRU entry and removes it if the cache is over capacity or the minimum timeout has elapsed. Destroy frees entries but deliberately does not release `fileinfo` objects; callers such as export release and DS cache clear do that.

State is in-memory only. Timestamps use `timespec_get(TIME_UTC)` converted to milliseconds. Persistence is the open SaunaFS fileinfo object referenced by entries.

Dependencies include Ganesha `glist`, `avltree`, allocation helpers, pthread mutexes, and SaunaFS C API types. Risks include no hard cap during acquire, reliance on callers to release `fileinfo`, assert-heavy misuse detection, duplicate entries possible for in-use same-inode handles, and time conversion naming using nanoseconds divided by a microsecond constant. Test signals should cover concurrent acquire/release, duplicate inode use, timeout expiry, max-entry pressure, erase-on-open-failure, and destroy after drained cache.
