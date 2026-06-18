# File Research: sources/os/linux/linux-stable/fs/ntfs3/ntfs_fs.h

Purpose: Central NTFS3 in-memory interface. It defines mount/inode/run/index state and declares the cross-file API surface for NTFS3 implementation modules.

Key contents:
- Mount options for ownership, masks, character conversion, sparse/prealloc/discard behavior, case sensitivity, hidden/meta visibility, Windows-name validation, delayed allocation, and forced dirty mounts.
- In-memory extent/run representation with `struct runs_tree` and `RUN_DEALLOCATE`.
- `struct wnd_bitmap` for free-space bitmaps, including window-level free counts, rb-tree extent indexes, zone tracking, and synchronization state.
- `struct ntfs_sb_info` with cluster/block geometry, record/index sizing, MFT state, global cluster bitmap, volume metadata, `$Secure`, `$Reparse`, `$ObjId`, compression contexts, mount options, proc entry, and ratelimited logging state.
- `struct mft_inode` and `struct ntfs_inode`, which embed the base MFT record, VFS inode, valid size, creation time, standard attributes, subrecord tree, directory or file run state, attribute-list state, and NTFS-specific flags.
- Function prototypes for attribute handling, attrlist handling, bit operations, directory/name/file operations, frecord/inode logic, log replay, low-level NTFS I/O/security/reparse/object-id helpers, index handling, runlist handling, superblock helpers, bitmap handling, upcase comparisons, xattrs/ACLs, and compression.

Important invariants:
- `ntfs_inode::ni_lock` has explicit nested lock classes for normal, parent, security, object-id, reparse, and dirty contexts.
- File run state uses `run_lock`; directory index state uses per-index run locks and version counters.
- Delayed allocation is tracked per file and globally through atomic `sbi->used.da`.
- Time conversion uses NTFS 100 ns units with signed arithmetic on decode to support pre-1970 timestamps.
- `is_ntfs3()` gates NTFS 3.x metadata features such as `$Secure`, `$Extend`, `$Reparse`, and `$ObjId`.

Dependencies:
- Includes `ntfs.h` for all on-disk layouts.
- Declares interfaces implemented by `attrib.c`, `attrlist.c`, `bitmap.c`, `dir.c`, `file.c`, `frecord.c`, `fslog.c`, `fsntfs.c`, `index.c`, `inode.c`, `namei.c`, `record.c`, `run.c`, `super.c`, `upcase.c`, `xattr.c`, and compression modules.

Risk notes:
- This header is a high-coupling point; changing structures affects most NTFS3 files.
- Many declared APIs rely on caller-held inode/run/index locks that are not encoded in types.
- The run tree is array-backed with a TODO to use rb-trees; memory growth and fragmentation are controlled by implementation policy in `run.c`.
