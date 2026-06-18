# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/denode.h

## Purpose
Defines the in-memory FAT directory-entry node (`denode`), vnode conversion macros, FAT cache structures, internal/external directory-entry conversion macros, file-handle layout, flags, and msdosfs vnode/internal service prototypes.

## Main Contents
- Documents FAT directory-entry quirks: reserved clusters, special root directory behavior, cluster 0 semantics, directory size conventions, and missing on-disk link counts.
- `MSDOSFSROOT_OFS` defines a synthetic root directory entry offset.
- `struct fatcache` and `FC_*` constants cache recent file-relative to filesystem-relative cluster mappings.
- `struct msdosfs_lookup_results` stores lookup side results used by create/remove paths.
- `struct denode_key` identifies vcache entries by directory cluster, directory offset, and unlink generation.
- `struct denode` embeds `genfs_node`, vnode/device/mount pointers, flags, refcount, lockf list, DOS 8.3 name, attributes, timestamps, start cluster, file size, and FAT cache.
- `DE_INTERNALIZE`/`DE_EXTERNALIZE` convert between on-disk `direntry` and in-memory `denode`, including FAT32 high-cluster bits.
- `VTODE`/`DETOV` convert vnode and denode pointers.
- `DETIMES` processes pending timestamp flags.
- `struct defid` overlays file handles.
- Declares vnode operations and internal helpers for update, create, extend, get, truncate, read/remove directory entries, unique DOS names, FAT-backed genfs allocation, and file-handle generation tracking.

## Dependencies
Uses genfs in kernel builds, or stub declarations under `MAKEFS`. Depends on `direntry.h`, `bpb.h`, `fat.h`, `msdosfsmount.h`, and NetBSD vnode/buffer/credential types through including context.

## Risks and Notes
`de_refcnt` is an in-memory substitute for missing FAT link counts and is central to deletion behavior. Directory entry conversion macros are multi-expression macros with side effects and depend on `FAT32(dep->de_pmp)`. `de_dirgen` exists for unlinked nodes but normal vcache keys assert it is null in `msdosfs_loadvnode()`.
