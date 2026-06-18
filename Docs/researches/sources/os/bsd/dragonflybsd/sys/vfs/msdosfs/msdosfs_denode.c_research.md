# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_denode.c

## Scope

Implements MSDOSFS denode hash caching, denode creation/loading, directory-entry updates, file truncation/extension, inactive handling, and reclaim.

## APIs And Behavior

- `msdosfs_init()` and `msdosfs_uninit()` allocate/free the global denode hash.
- `msdosfs_hashget()`, `msdosfs_hashins()`, `msdosfs_hashrem()`, and `msdosfs_reinsert()` manage cached denodes under `dehash_token`.
- `deget()` returns a locked denode by directory cluster/offset, manufactures the root denode, reads disk directory entries for normal files, initializes vnode type, VM object, device vnode ref, refcount, FAT cache, and directory size.
- `deupdat()` writes modified denode metadata back to its directory entry, applying pending timestamp updates and choosing synchronous, async, or delayed buffer writes.
- `detrunc()` truncates files/directories, handles root restrictions, zeroes partial clusters, updates file size, breaks FAT chains, purges FAT cache, writes directory metadata, and frees trailing clusters.
- `deextend()` grows regular files by allocating clusters and updating metadata.
- `msdosfs_inactive()` truncates deleted open files on writable mounts, updates metadata, and recycles stale/deleted denodes.
- `msdosfs_reclaim()` removes denodes from the hash and frees device vnode references.

## Dependencies

Depends on vnode/buffer/VM APIs, `denode.h`, `direntry.h`, `fat.h`, mount state, and FAT allocation/free helpers.

## Risks And Invariants

The hash ignores deleted/unlinked denodes for lookup via `de_refcnt > 0`. Truncation must update both FAT chains and vnode buffers. Root directory truncation is illegal on FAT12/16. Directory sizes are computed by walking FAT chains because DOS directory entries store zero size.
