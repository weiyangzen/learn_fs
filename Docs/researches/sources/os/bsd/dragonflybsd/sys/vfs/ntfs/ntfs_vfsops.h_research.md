# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.h

This header defines flags for `ntfs_vgetex()`: `VG_DONTLOADIN`, `VG_DONTVALIDFN`, and `VG_EXT`. These control whether to load the `ntnode`, validate the `fnode`, and treat a record as an external/non-main record.

It declares `ntfs_vgetex()` and `ntfs_calccfree()`.

Research notes: these flags are used by directory lookup and attribute-list traversal to instantiate partial or external vnode state without forcing all normal validation paths.
