# File Research: sources/os/linux/linux/fs/afs/dir_search.c

Purpose: provides hash-based lookup into cached AFS directory contents.

Key interfaces:
- `afs_dir_hash_name()`.
- `afs_dir_init_iter()`.
- `afs_dir_find_block()`.
- `afs_dir_search_bucket()`.
- `afs_dir_search()`.

Implementation notes:
- Hash function multiplies by 173 and maps into the fixed AFS directory hash table, with special handling for signed overflow semantics.
- Iterator setup computes required name slots, target bucket, maximum loop count, and previous-entry state.
- `afs_dir_find_block()` maps the folio containing a directory block and unmaps any previous mapped block.
- Bucket search starts from block 0 hashtable bucket, follows `hash_next`, validates reserved slot ranges, compares NUL-terminated names, returns vnode/unique on match, and tracks predecessor for edit/remove.
- Loop count limits prevent infinite traversal on corrupt hash chains.
- `afs_dir_search()` ensures the directory is read and valid, captures inode i_version as directory version, searches the bucket, unlocks validation, and retries a few times on stale data.

Dependencies:
- AFS directory folio queue, validation lock from `afs_read_dir()`, directory invalidation, XDR directory structures.

Edge cases:
- Empty directories return `-ENOENT`.
- Missing or invalid blocks invalidate the directory and return `-ESTALE`.
- Deleted vnode during retry stops with `-ESTALE`.
