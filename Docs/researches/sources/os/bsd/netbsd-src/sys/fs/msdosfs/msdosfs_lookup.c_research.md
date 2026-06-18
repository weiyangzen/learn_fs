# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_lookup.c

## Summary
Implements msdosfs directory lookup, directory-entry creation/removal helpers, directory emptiness checks, short-name collision generation, and Win95 long-name discovery. It bridges VFS pathname operations with FAT directory entry layout, including 8.3 aliases and long filename slot sequences.

## Main Responsibilities
- Perform `VOP_LOOKUP` for msdosfs directories, including access checks, name-cache lookup/insert, root `.`/`..` synthesis, short-name conversion, long-name checksum matching, slot discovery, and create/rename/delete result setup.
- Install new directory entries with `msdosfs_createde()`, extending directories as needed and writing Win95 long-name slots before the DOS entry.
- Roll back partially written long-name entries by marking slots deleted if directory-entry creation fails after modifications begin.
- Test directories for emptiness with `msdosfs_dosdirempty()`, ignoring deleted entries, volume labels, `.` and `..`.
- Read directory entries by parent cluster/offset through `msdosfs_readep()` and by denode through `msdosfs_readde()`.
- Remove directory entries and preceding long-name slots with `msdosfs_removede()`, including denode refcount handling and vcache rekeying for removed objects.
- Generate unique 8.3 aliases with `msdosfs_uniqdosname()`.
- Detect whether a directory appears to contain Win95 long filename entries via `msdosfs_findwin95()`.

## Key Interfaces
- `msdosfs_lookup(void *)`.
- `msdosfs_createde(struct denode *, struct denode *, const struct msdosfs_lookup_results *, struct denode **, struct componentname *)`.
- `msdosfs_dosdirempty(struct denode *)`.
- `msdosfs_readep(struct msdosfsmount *, u_long, u_long, struct buf **, struct direntry **)`.
- `msdosfs_readde(struct denode *, struct buf **, struct direntry **)`.
- `msdosfs_removede(struct denode *, struct denode *, const struct msdosfs_lookup_results *)`.
- `msdosfs_uniqdosname(struct denode *, struct componentname *, u_char *)`.
- `msdosfs_findwin95(struct denode *)`.

## Risks
Lookup result state is stored in the parent denode's `de_crap` and remains valid only while the directory lock discipline is respected. Negative name caching is disabled because case-insensitive and 8.3 alias behavior would make invalidation unsafe. Directory-entry creation and removal span multiple directory slots and sometimes multiple blocks, so failures can leave deleted or orphaned long-name slots. `msdosfs_removede()` intentionally deletes any preceding Win95 entries it sees, not only those proven to belong to the short entry. Directory scanning depends on FAT semantics where `SLOT_EMPTY` terminates the used directory region.
