# File Research: sources/os/linux/linux-stable/fs/inode.c

This file implements the core Linux VFS inode cache: inode allocation, initialization, hashing, lookup, reference release, LRU reclaim, eviction, timestamps, ownership helpers, direct-I/O waiting, and init-time inode cache setup.

Key responsibilities:
- Defines inode cache locking rules and lock ordering across inode state, superblock inode lists, inode LRU, writeback lists, and the global inode hash.
- Initializes every inode in `inode_init_always_gfp()`, including operations, mapping state, ACL/fsnotify/security fields, writeback state, counters, locks, and address-space defaults.
- Provides inode allocation/free paths: `alloc_inode()`, `new_inode()`, `destroy_inode()`, and RCU-delayed freeing.
- Maintains link count helpers: `drop_nlink()`, `clear_nlink()`, `set_nlink()`, and `inc_nlink()`, including `s_remove_count` accounting.
- Initializes address spaces and inodes once per slab object via `address_space_init_once()` and `inode_init_once()`.
- Manages inode LRU insertion, removal, isolation, page-cache reclaim from inode mappings, and superblock shrinker support in `prune_icache_sb()`.
- Implements inode hash insertion/removal and lookup APIs: `iget_locked()`, `iget5_locked()`, `iget5_locked_rcu()`, `ilookup()`, `ilookup5()`, `find_inode_nowait()`, `find_inode_rcu()`, and `find_inode_by_ino_rcu()`.
- Handles races with `I_NEW`, `I_CREATING`, `I_FREEING`, and `I_WILL_FREE` through wait queues and retry loops.
- Implements `iput()` and `iput_final()`, including lazytime sync retry, drop decisions, LRU retention, forced writeout, and eviction.
- Provides `bmap()` for block filesystems when `CONFIG_BLOCK` is enabled.
- Implements atime, mtime, ctime, lazytime, i_version, and multigrain timestamp handling.
- Provides write modification helpers: `file_remove_privs()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()`.
- Initializes inode hash tables and the inode slab cache via `inode_init_early()` and `inode_init()`.
- Provides special inode setup, inode owner initialization, owner/capability checks, SGID stripping, no-highmem mapping setup, and direct-I/O wait helpers.

Important interactions:
- Touches core VFS objects: `super_block`, `inode`, `address_space`, `dentry`, `vfsmount`, writeback state, security hooks, fsnotify, ACLs, fsverity, cdev/block/pipe file operations, and debugfs/sysctl reporting.
- Exports many symbols used by filesystems throughout the kernel tree.
- Coordinates with memory reclaim via `list_lru`, `invalidate_mapping_pages()`, and inode shrinker callbacks.
- Coordinates with writeback through inode dirty state, lazytime, `inode_wait_for_writeback()`, and writeback list removal.

Notable invariants and risks:
- `inode->i_lock` protects inode state transitions; multiple paths rely on state checks plus wait-bit wakeups to avoid use-after-free or duplicate inode instantiation.
- `I_NEW` must be cleared by `unlock_new_inode()` or discarded via `discard_new_inode()`.
- Inode LRU eligibility requires zero refcount, clean state, active superblock, and shrinkable mapping.
- `iput()` can sleep and can trigger full filesystem eviction paths.
- Multigrain timestamp logic uses atomic nanosecond compare/exchange and the `I_CTIME_QUERIED` bit; correctness depends on ordering between ctime sec/nsec fields and query/update paths.
- The file contains broad VFS infrastructure, so small behavioral changes can affect nearly every filesystem.

Research notes:
- This is one of the central VFS lifecycle files. Its critical themes are object lifetime, lookup race handling, shrinker behavior, and timestamp/write-side metadata consistency.
