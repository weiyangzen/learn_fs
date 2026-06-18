# File Research: sources/os/linux/linux/fs/inode.c

Core VFS inode implementation. This file owns generic inode allocation, initialization, hashing, lookup, refcounting, LRU reclaim, eviction, timestamp updates, permission-related write side effects, inode-number generation, and inode cache initialization.

Major responsibilities:
- Defines and exports `empty_aops`, inode counters, inode sysctls, and optional multigrain timestamp debugfs counters.
- Initializes each inode via `inode_init_always_gfp()` and once-per-slab state via `inode_init_once()`.
- Provides generic inode allocation/freeing through `alloc_inode()`, `new_inode()`, `destroy_inode()`, and RCU delayed freeing.
- Manages link-count helpers `drop_nlink()`, `clear_nlink()`, `set_nlink()`, and `inc_nlink()` while tracking pending removals.
- Maintains inode hash table with `__insert_inode_hash()`, `__remove_inode_hash()`, `iget_locked()`, `iget5_locked()`, `ilookup*()`, `find_inode*()`, and `insert_inode_locked*()`.
- Implements inode LRU and shrinker integration through `inode_lru_list_add()`, `prune_icache_sb()`, `evict_inodes()`, and `evict()`.
- Handles final reference release in `iput()` and `iput_final()`, including lazytime sync and filesystem `drop_inode()` policy.

Timestamp and write-side policy:
- `atime_needs_update()` and `touch_atime()` enforce mount/inode noatime, relatime, nodiratime, idmap, and read-only constraints.
- `inode_update_time()`, `generic_update_time()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()` update atime/mtime/ctime and i_version.
- `current_time()`, `inode_set_ctime_current()`, and `inode_set_ctime_deleg()` implement multigrain timestamp behavior.
- `file_remove_privs()` removes suid/sgid/capability privilege state on writes.

Other exported helpers:
- `bmap()`, `init_special_inode()`, `inode_init_owner()`, `inode_owner_or_capable()`, `mode_strip_sgid()`, `inode_dio_wait()`, `inode_set_flags()`, `inode_nohighmem()`, and `timestamp_truncate()`.

Concurrency and invariants:
- Lock ordering is documented at the top and spans superblock inode list lock, inode `i_lock`, inode LRU locks, writeback locks, and inode hash lock.
- Lookup paths handle `I_NEW`, `I_CREATING`, `I_FREEING`, and `I_WILL_FREE` carefully, including wait queues on inode state bits.
- Eviction requires `I_FREEING`, no LRU membership, completed writeback, page-cache cleanup, hash removal, and wakeup of waiters.
- Refcount transitions in `igrab_from_hash()` and `unlock_new_inode()` rely on memory barriers.
