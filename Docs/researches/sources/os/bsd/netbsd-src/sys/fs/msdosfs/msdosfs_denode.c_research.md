# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_denode.c

## Purpose
Implements msdosfs denode pool lifecycle, vnode loading through vcache, file truncation/extension, vnode inactive/reclaim behavior, genfs update hooks, and an in-memory file-handle generation map.

## Main Entry Points
- `msdosfs_init()` attaches malloc types, initializes the denode pool, file-handle pool, red-black tree, and lock.
- `msdosfs_done()` destroys pools, lock, and malloc types.
- `msdosfs_deget()` normalizes FAT32 root cluster keys and resolves denodes through `vcache_get()`.
- `msdosfs_loadvnode()` allocates a denode, manufactures the root directory entry or reads an on-disk directory entry, internalizes FAT fields, determines vnode type, computes directory size, references the device vnode, initializes genfs/UBC state, and returns the cache key.
- `msdosfs_deupdat()` calls `msdosfs_update()` for pending directory-entry metadata writes.
- `msdosfs_detrunc()` shrinks files or directories, updates UVM size, zeroes partial trailing cluster data, writes updated directory metadata, purges FAT cache, breaks FAT chains, and frees removed clusters.
- `msdosfs_deextend()` grows regular files by allocating clusters, zero-filling the new range, updating UVM write size, and writing metadata.
- `msdosfs_reclaim()` releases the device vnode, destroys genfs state, clears vnode data under interlock, and returns the denode to the pool.
- `msdosfs_inactive()` truncates deleted unreferenced files on writable mounts, marks slots deleted, removes file-handle mappings, updates metadata, and requests recycle.
- `msdosfs_gop_alloc()` is a no-op allocation hook.
- `msdosfs_gop_markupdate()` maps genfs accessed/modified flags to denode timestamp flags.
- `msdosfs_fh_enter()`, `msdosfs_fh_remove()`, `msdosfs_fh_lookup()`, and `msdosfs_fh_destroy()` maintain generation numbers in a locked red-black tree keyed by mount, directory cluster, and directory offset.

## Dependencies
Uses NetBSD vnode cache, pool allocator, red-black tree, mutexes, UVM, buffer cache, genfs, kauth, FAT helpers, BPB helpers, directory-entry conversion macros, and mount state from `msdosfsmount.h`.

## Risks and Notes
`msdosfs_loadvnode()` relies on FAT chain traversal to synthesize directory sizes because FAT directory entries store zero size for directories. `msdosfs_detrunc()` sets UVM size before some error paths, so callers depend on later recovery or consistency assumptions. The file-handle generation counter is global and monotonically increments without persistence, so it prevents stale handles only within the running kernel lifetime. `msdosfs_gop_alloc()` returns success without allocating, which is intentional only if allocation is handled by higher write/truncate paths.
