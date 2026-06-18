# File Research: sources/os/linux/linux/fs/dcache.c

## Role

Implements the Linux VFS dentry cache: allocation, hashing, lookup, aliasing, dentry reference release, LRU/shrinker integration, subtree pruning, rename/move handling, disconnected/root aliases, temporary dentries, and early VFS cache initialization.

This is a core VFS file. It mediates between pathname lookup, inode lifetime, filesystem-specific `dentry_operations`, mount handling, exportable filesystem aliases, and memory reclaim.

## Major Responsibilities

- Maintains the global dentry hash table and per-parent name lookup path.
- Provides RCU-walk and refcounted lookup APIs: `__d_lookup_rcu()`, `__d_lookup()`, `d_lookup()`, `d_hash_and_lookup()`.
- Allocates dentries through `__d_alloc()`, `d_alloc()`, `d_alloc_anon()`, `d_alloc_pseudo()`, and cursor allocation.
- Binds dentries to inodes through `d_instantiate()`, `d_instantiate_new()`, `d_add()`, `d_make_root()`, `d_obtain_alias()`, `d_obtain_root()`, and `d_splice_alias()`.
- Handles reference dropping and eviction via `dput()`, `fast_dput()`, `dentry_kill()`, and `dentry_free()`.
- Maintains LRU and shrink lists, including negative-dentry accounting.
- Walks and prunes dentry subtrees for unmount, invalidation, and memory pressure.
- Implements dentry rename/exchange mechanics under `rename_lock`.
- Initializes VFS caches through `vfs_caches_init_early()` and `vfs_caches_init()`.

## Key Data and State

- `rename_lock`: exported sequence lock protecting rename/move topology observations.
- `dentry_hashtable`: global hash table for normal dentries.
- `in_lookup_hashtable`: temporary hash table for parallel in-progress lookups.
- Per-CPU counters:
  - `nr_dentry`
  - `nr_dentry_unused`
  - `nr_dentry_negative`
- Sysctls:
  - `vm.vfs_cache_pressure`
  - `vm.vfs_cache_pressure_denom`
  - `fs.dentry-state`
  - `fs.dentry-negative`
- Exported qstr constants:
  - `empty_name`
  - `slash_name`
  - `dotdot_name`

## Locking Model

The file documents and enforces a strict hierarchy:

- `inode->i_lock` protects inode alias lists and `d_alias`.
- dentry hash bucket locks protect hash membership.
- `s_roots_lock` protects secondary root lists.
- `s_dentry_lru` protects LRU accounting.
- `dentry->d_lock` protects dentry flags, name, parent/child links, refcount, hash state, inode pointer, and alias fields.
- Parent dentry locks precede child dentry locks when an ancestor relationship exists.
- Unrelated topology changes are serialized or detected through `rename_lock`.

RCU and seqcount use is central. Many lookups intentionally tolerate false negatives, but not unsafe positive results.

## Dentry Names

Short names are stored inline in `d_shortname`; long names use `struct external_name` with refcounting and RCU-delayed freeing. `take_dentry_name_snapshot()` safely snapshots names across concurrent rename by combining RCU, `d_seq`, and external-name refcounts.

Name comparison is optimized with `CONFIG_DCACHE_WORD_ACCESS` using word-at-a-time loads, while still preserving safety for unaligned pathname input.

## Lifetime and Eviction

`dput()` uses a fast lockref path first. If the last reference is dropped and the dentry cannot be retained, `finish_dput()` calls `dentry_kill()`.

`dentry_kill()`:

- Verifies the dentry is idle.
- Marks the lockref dead.
- Calls `d_prune()` when present.
- Removes the dentry from LRU/hash state.
- Detaches the inode through `dentry_unlink_inode()`.
- Runs `d_release()`.
- Removes the dentry from the parent tree.
- Frees immediately or leaves final freeing to shrink-list owner.

`lock_for_kill()` handles the difficult `d_lock` versus `inode->i_lock` ordering problem by using trylock first, then an RCU-protected lock handoff path.

## LRU and Shrinker Integration

LRU helpers consistently maintain dentry flags and per-CPU counters:

- `d_lru_add()`
- `d_lru_del()`
- `d_shrink_add()`
- `d_shrink_del()`
- `d_lru_isolate()`
- `d_lru_shrink_move()`

Memory reclaim paths include:

- `prune_dcache_sb()`
- `shrink_dcache_sb()`
- `shrink_dentry_list()`
- `d_prune_aliases()`

Negative dentries are counted only while on the real superblock LRU, avoiding useless count churn when entries move to temporary shrink lists.

## Tree Walking and Pruning

`d_walk()` is the central dentry-tree walker. It handles cursor dentries, rename retries, and ascent/descent without recursive stack growth.

Used by:

- `path_has_submounts()`
- `shrink_dcache_parent()`
- `shrink_dcache_for_umount()`
- `d_invalidate()`

`shrink_dcache_tree()` handles races with dentries already being killed by using waiter completions attached through `dentry->waiters`.

Unmount cleanup uses `do_one_tree()` and `shrink_dcache_for_umount()` to discard root and secondary-root dentries, checking for busy leaves.

## Lookup Paths

The file provides two major lookup styles:

- RCU/store-free lookup:
  - `__d_lookup_rcu()`
  - `__d_lookup_rcu_op_compare()`
- Refcounted lookup:
  - `__d_lookup()`
  - `d_lookup()`

`d_lookup()` wraps `__d_lookup()` in `rename_lock` retry logic to avoid false negatives caused by concurrent rename.

`d_hash_and_lookup()` applies standard hashing plus optional filesystem-specific `d_hash()` before lookup.

`d_same_name()` delegates to filesystem-specific `d_compare()` when needed.

## Parallel Lookup

`d_alloc_parallel()` supports concurrent lookup of the same missing child. It creates an in-lookup dentry marked `DCACHE_PAR_LOOKUP`, checks both normal dcache and in-lookup hash, waits on competing lookups when necessary, and uses `i_dir_seq` plus `rename_lock` to detect directory changes.

Completion helpers:

- `__d_lookup_unhash()`
- `__d_wake_in_lookup_waiters()`
- `__d_lookup_unhash_wake()`

`__d_add()` completes an in-lookup dentry by removing it from the in-lookup hash, adding optional operations, binding inode state, rehashing, updating directory sequence, and waking waiters.

## Inode Aliases and Export Support

Alias helpers include:

- `d_find_any_alias()`
- `d_find_alias()`
- `d_find_alias_rcu()`
- `d_obtain_alias()`
- `d_obtain_root()`
- `d_splice_alias()`
- `d_splice_alias_ops()`

Directory aliases are tightly controlled because directories may not have multiple normal aliases. `d_splice_alias_ops()` can move disconnected/root aliases into the live tree and rejects loops with `-ELOOP`.

This is essential for exportable filesystems and NFS filehandle reconstruction.

## Rename and Move

`__d_move()` performs the core dentry topology update:

- Locks old and new parents in topology-safe order.
- Handles target dentries that are still in lookup.
- Invalidates hash entries.
- Swaps or copies names depending on exchange mode.
- Updates child lists, parents, hash membership, fsnotify state, and fscrypt move state.
- Uses `d_seq` updates for RCU path-walk correctness.

Public wrappers:

- `d_move()`
- `d_exchange()`

`is_subdir()` checks ancestry with `rename_lock` retry and falls back to exclusive sequence lock for progress.

## Temporary and Persistent Dentries

- `d_make_persistent()` instantiates and pins a dentry, used by pseudo filesystems such as debugfs/devpts.
- `d_make_discardable()` drops the persistent pin and resumes normal dput eviction.
- `d_mark_tmpfile()`, `d_mark_tmpfile_name()`, and `d_tmpfile()` support temporary file naming and instantiation.

## Initialization

`dcache_init_early()` optionally allocates the dentry hash table early unless NUMA hash distribution delays allocation.

`dcache_init()` creates the dentry slab cache and allocates the hash table when needed.

`vfs_caches_init_early()` initializes in-lookup hash buckets, dcache, and inode early state.

`vfs_caches_init()` initializes filename, dcache, inode, file table, mount, block-device, and character-device caches.

## Important Invariants

- A live dentry pins its inode; dcache is a master of icache lifetime.
- Dentries visible to RCU must be freed with RCU delay unless marked `DCACHE_NORCU`.
- A dentry in `DCACHE_PAR_LOOKUP` is not complete for normal lookup.
- Negative-dentry counters only track real LRU membership.
- Directory inodes should have only one alias.
- Callers must not touch dentries after handing them to `dentry_kill()`.

## Research Notes

This file is foundational for VFS pathname correctness. The highest-risk areas are lock ordering, RCU/seqcount pairing, hash membership transitions, shrinker races, and directory alias moves. Many functions are exported and used widely by pseudo filesystems, local filesystems, network filesystems, and VFS core lookup code.
