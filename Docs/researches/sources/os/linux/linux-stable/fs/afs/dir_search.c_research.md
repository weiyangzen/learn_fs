# File Research: sources/os/linux/linux-stable/fs/afs/dir_search.c

## Summary
Implements lookup of names inside locally cached AFS directory data. It hashes names into AFS directory hash buckets, locates directory blocks in the vnode's folio queue, walks hash chains, and returns the matching file identifier plus directory data version.

## Main Responsibilities
- Computes AFS directory name hash buckets with `afs_dir_hash_name()`.
- Initializes and resets `struct afs_dir_iter` for a lookup.
- Maps a requested AFS directory block from `dvnode->directory`.
- Walks one directory bucket chain and detects corrupt chains.
- Coordinates directory reread/retry behavior around stale or invalid directory contents.

## Key APIs
- `afs_dir_hash_name()`.
- `afs_dir_init_iter()`.
- `afs_dir_find_block()`.
- `afs_dir_search_bucket()`.
- `afs_dir_search()`.

## Important Behavior
`afs_dir_find_block()` reuses the iterator's current folio queue position when possible, but rewinds to the start if the requested block is before the current position. If a block cannot be found or mapped consistently, it invalidates the directory with `afs_invalidate_dir()`.

`afs_dir_search_bucket()` starts from the directory metadata block's hash table, validates reserved slot boundaries, compares the inline directory entry name including NUL termination, and returns the raw directory entry index on success. It decrements `loop_check` on each chain step to detect loops.

`afs_dir_search()` calls `afs_read_dir()` and retries up to three times on `-ESTALE`, unless the directory vnode is already marked deleted. It records the raw inode version as the directory version after a successful read.

## State and Synchronization
`afs_read_dir()` is expected to acquire `dvnode->validate_lock`; this file releases that read lock after bucket search. Directory validity is tracked through `AFS_VNODE_DIR_VALID` and explicit invalidation reasons.

## Risks
Directory corruption or stale folio queue state is treated as `-ESTALE` and invalidates the cached directory. The code relies on AFS directory layout constants and careful slot arithmetic; incorrect reserved-slot handling would misinterpret metadata as entries.
