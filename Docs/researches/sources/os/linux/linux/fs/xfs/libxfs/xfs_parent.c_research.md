# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.c

This file implements XFS parent pointer attributes. Parent pointers are stored as local extended attributes whose name is the directory entry name and whose value is a `struct xfs_parent_rec` containing parent inode number and generation.

Major responsibilities:
- Validate parent pointer attr names with `xfs_parent_namecheck`.
- Validate parent pointer values with `xfs_parent_valuecheck`.
- Compute parent pointer hash values with parent inode mixed into the directory name hash.
- Initialize `xfs_da_args` for parent pointer xattr operations.
- Ensure attr fork extents are loaded before parent pointer operations.
- Add, remove, and replace parent pointers for link/unlink/rename operations.
- Extract parent inode/generation from xattr data.
- Provide repair-oriented lookup/set/unset helpers.

Important behavior:
- Parent pointers require the parent feature to be enabled.
- Names must satisfy directory filename constraints and cannot be incomplete attrs.
- Values must be local, non-null, exactly `sizeof(struct xfs_parent_rec)`, and contain a valid directory inode.
- Parent pointer attrs use `XFS_ATTR_PARENT`, logged operations, and OKNOENT behavior.
- Hashing mixes parent inode with name hash to reduce hardlink collision risk.
- Parent pointer updates call into attr set/remove/replace machinery.

Repair helpers:
- `xfs_parent_lookup` looks up a specific parent pointer under caller-held inode lock.
- `xfs_parent_set` and `xfs_parent_unset` are immediate, no-transaction repair functions and sanity-check inputs first.

Risk notes:
- Missing attr fork on a parent-enabled child is treated as corruption and marks inode parent health sick.
- Creating inodes without required parent pointers is considered corruption-prone; other code reserves blocks accordingly.
- Correct generation handling matters to distinguish reused inode numbers.
