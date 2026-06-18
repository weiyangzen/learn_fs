# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.h

Defines shared state, constants, and internal data structures for `mkfs.ocfs2`.

Key contents:
- Mount modes: local vs cluster.
- Formatting constants for reserved blocks, clear size, default OCFS2 policy values, block discard step.
- `SystemFileInfo`: static description of OCFS2 system files.
- `AllocGroup`: in-memory allocation group descriptor plus chain accounting.
- `SystemFileDiskRecord`: planned on-disk inode/extent/allocation metadata for a system file.
- `AllocBitmap`: global bitmap/group construction state.
- `DirData`: temporary directory buffer plus linked disk record.
- `State`: full formatter state from CLI, feature flags, geometry, cluster settings, allocator state, and filesystem type.

Declared functions:
- `is_classic_stack`
- `cluster_fill`
- `ocfs2_fill_cluster_information`
- `ocfs2_check_volume`

Dependencies:
- Standard C/POSIX headers.
- `uuid/uuid.h`, `ocfs2/ocfs2.h`, `ocfs2/bitops.h`, OCFS1 compatibility header.

Research notes:
- This header is local to `mkfs.ocfs2`; it exposes the contract between `mkfs.c` and `check.c`.
- `State` is the central object that carries parsed user intent and computed filesystem geometry through the formatter.
