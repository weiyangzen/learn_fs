# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_denode.c

Implements denode lifecycle and file-size mutation for msdosfs: vnode lookup/allocation, directory-entry synchronization, truncation, extension, hash reinsertion, inactive processing, and reclaim.

Main responsibilities:
- `deget()` obtains or creates a denode/vnode for a directory-entry location.
- `deupdat()` writes modified denode metadata back to its on-disk directory entry.
- `detrunc()` truncates files and frees trailing cluster chains.
- `deextend()` allocates clusters and extends regular files.
- `reinsert()` updates the vnode hash key after a file moves to a new directory entry.
- `msdosfs_inactive()` handles final cleanup of deleted files.
- `msdosfs_reclaim()` removes denodes from the vnode hash and frees memory.

Key implementation details:
- Denodes are hashed by synthetic inode from `DETOI()`, with `de_vncmpf()` rejecting unlinked/open entries with nonpositive refcount.
- Root denodes are manufactured because FAT root directories may lack real directory entries. Non-FAT32 root has fixed size; FAT32 root behaves more like a normal cluster chain.
- Directory denode size is derived by walking the FAT chain with `pcbmap()` because directory entries store zero size for directories.
- `deupdat()` applies pending FAT timestamp changes via `DETIMES()`, externalizes the denode to a `direntry`, and writes or delays the directory block.
- `detrunc()` protects fixed FAT12/16 root directories, zero-fills partial final clusters, updates file size and directory entry, truncates vnode buffers, breaks the FAT chain, and frees removed clusters.
- `deextend()` refuses directories and fixed root extension, allocates required clusters with `extendfile()`, clears partial buffers at old EOF for large cluster/page interactions, updates vnode pager size, and writes metadata.
- `msdosfs_inactive()` truncates deleted read/write files to zero, marks the directory entry deleted, and recycles deleted/empty denodes.

Important dependencies:
- FAT mapping/allocation routines from `fat.h`.
- Directory entry conversion macros from `denode.h`.
- Buffer cache, vnode hash, VM page pressure, and vnode pager APIs.

Notable risks and edge cases:
- Root handling differs between FAT32 and older FAT variants.
- Deleted but still open files must not be reused from the denode hash even if their directory slot is reused.
- Extension has a rollback path through `detrunc()` if allocation or buffer clearing fails.
