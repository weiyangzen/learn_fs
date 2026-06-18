# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/denode.h

## Scope

Defines the in-memory MSDOSFS denode, FAT cache, denode flags, directory-entry conversion macros, timestamp update macro, filehandle layout, and internal denode service prototypes.

## Data Structures And APIs

- Documents FAT directory semantics and root-directory special cases.
- Defines root pseudo-offset `MSDOSFSROOT_OFS`.
- `struct fatcache` and cache slots `FC_LASTMAP`, `FC_LASTFC`, `FC_NEXTTOLASTFC` speed FAT chain traversal and extension.
- `struct denode` stores hash linkage, vnode/device identity, directory-entry location, lookup offsets, refcount, mount pointer, DOS directory-entry metadata, FAT cache, and revision counter.
- Defines flags for pending update/create/access timestamps, modified state, and rename.
- `DE_INTERNALIZE` and `DE_EXTERNALIZE` convert between disk `direntry` and in-memory `denode`, including FAT32 high cluster bits.
- `DETIMES` updates FAT timestamps and archive bit.
- Declares denode lifecycle, directory-entry, truncate, create/remove, path-check, and FAT use-map helpers.

## Dependencies

Depends on BPB, directory-entry, FAT, mount, vnode, and endian helpers.

## Risks And Invariants

Denodes are keyed by directory-entry location, not only starting cluster. Deleted-but-open files can remain cached with nonpositive `de_refcnt`. Root directory handling differs between FAT12/16 and FAT32.
