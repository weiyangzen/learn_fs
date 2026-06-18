# File Research: sources/os/linux/linux-stable/fs/dcache.c

## Purpose

`dcache.c` implements the Linux VFS dentry cache: dentry allocation, lookup, hashing, aliasing, pruning, RCU path-walk support, rename/move mechanics, dentry lifetime management, and early VFS cache initialization.

## Main Responsibilities

- Maintains the global dentry hash table and in-progress parallel lookup hash table.
- Implements dentry reference release and final destruction through `dput()`, `__dentry_kill()`, and RCU-delayed freeing.
- Tracks unused and negative dentry counts with per-CPU counters and exposes dcache sysctls.
- Provides exported VFS helpers for dentry allocation, lookup, instantiation, deletion, invalidation, rename, alias splicing, and tmpfile naming.
- Manages dentry LRU and shrink-list transitions for reclaim and unmount.
- Supports lockless RCU path lookup through `__d_lookup_rcu()` and dentry sequence counts.
- Handles parallel lookup serialization through `d_alloc_parallel()`, `d_lookup_done()`-style unhash/wake helpers, and per-directory sequence updates.
- Initializes dcache slab and hash structures in `vfs_caches_init_early()` and `vfs_caches_init()`.

## Core Data and State

- `rename_lock`: global seqlock protecting rename-sensitive tree walks and lookup retry logic.
- `dentry_hashtable`: primary hash table keyed by parent/name hash.
- `in_lookup_hashtable`: temporary hash table for dentries under parallel lookup.
- Per-CPU counters: `nr_dentry`, `nr_dentry_unused`, and `nr_dentry_negative`.
- `struct external_name`: refcounted, RCU-freed storage for long names.
- Dentry flags such as `DCACHE_LRU_LIST`, `DCACHE_SHRINK_LIST`, `DCACHE_PAR_LOOKUP`, `DCACHE_DENTRY_KILLED`, `DCACHE_DISCONNECTED`, `DCACHE_DONTCACHE`, and type flags derived from inode mode.

## Key Control Flow

Lookup:
- `d_hash_and_lookup()` hashes a name, applies filesystem `d_hash`, then calls `d_lookup()`.
- `d_lookup()` wraps `__d_lookup()` with `rename_lock` retry protection.
- `__d_lookup_rcu()` performs store-free RCU lookup for path walking and returns a dentry plus sequence value that callers must validate.
- `d_same_name()` uses direct name comparison or filesystem `d_compare`.

Parallel lookup:
- `d_alloc_parallel()` first checks the normal hash under RCU, then checks the in-lookup hash, waits on an existing matching lookup if needed, or inserts a new `DCACHE_PAR_LOOKUP` dentry.
- `__d_add()` removes an in-lookup dentry from the temporary hash, wakes waiters, optionally instantiates an inode, and rehashes the dentry into the normal cache.

Lifetime and reclaim:
- `dput()` uses `fast_dput()` for the common lockref decrement path.
- When the last ref cannot be retained, `finish_dput()` and `__dentry_kill()` detach the dentry from hashes, aliases, parent children, LRU state, and inode.
- `shrink_dentry_list()`, `prune_dcache_sb()`, `shrink_dcache_sb()`, and `shrink_dcache_parent()` move unused dentries to local lists and destroy them.
- `shrink_dcache_for_umount()` tears down superblock root dentries and checks for still-busy dentries.

Rename and aliasing:
- `__d_move()` updates parents, names, child lists, hashes, fsnotify state, and fscrypt rename state under `rename_lock` and ordered dentry locks.
- `d_splice_alias_ops()` handles exportable filesystem lookup results, including disconnected directory aliases and loop prevention.
- `d_obtain_alias()` and `d_obtain_root()` create disconnected or root aliases from inodes.

## Important Dependencies

- VFS inode and mount internals from `internal.h` and `mount.h`.
- `list_lru` shrinker infrastructure.
- `lockref`, seqcount, RCU, hlist-bl locking, and superblock LRU state.
- Security hooks through `security_d_instantiate()`.
- fsnotify hooks for create, move, remove, and inode removal.
- fscrypt rename notification via `fscrypt_handle_d_move()`.

## Edge Cases and Risks

- Lock ordering is central: inode `i_lock`, dentry `d_lock`, superblock LRU lock, hash-bucket lock, and ancestor dentry locks must stay ordered as documented.
- RCU lookup intentionally tolerates false negatives but requires sequence validation before using returned dentry state.
- Negative dentry accounting only applies when a dentry is on the real LRU, not when on a shrink list.
- External dentry names are refcounted and RCU-freed; snapshots must release references exactly once.
- Directory aliases are constrained; `d_splice_alias_ops()` rejects alias moves that would create dcache loops.
- Parallel lookup depends on directory sequence updates and waitqueue wakeups to avoid duplicate lookup instantiation.
