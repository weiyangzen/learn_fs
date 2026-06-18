# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.c

## Role
`xfs_parent.c` implements XFS parent pointer attribute handling. Parent pointers are stored as special local xattrs whose name is the directory entry name and whose value is `struct xfs_parent_rec` containing parent inode number and generation.

## Main Responsibilities
- Validate parent pointer attribute names and values.
- Compute parent pointer attr hashes using directory name hash mixed with parent inode number.
- Initialize `xfs_da_args` for parent pointer xattr operations.
- Add, remove, and replace parent pointers during directory entry create/unlink/rename.
- Decode parent pointer information from raw xattr name/value pairs.
- Provide lookup, set, and unset helpers for repair code.

## Important Functions
- `xfs_parent_namecheck` rejects incomplete attrs and validates the name as a directory component.
- `xfs_parent_valuecheck` requires the parent feature, exact `xfs_parent_rec` value length, local value presence, and valid parent directory inode number.
- `xfs_parent_hashval` uses normal directory hash plus upper/lower parent inode bits to reduce hardlink collisions.
- `xfs_parent_hashattr` derives the same hash from xattr name/value components.
- `xfs_parent_da_args_init` sets up attr fork, parent attr filter, logged operation flags, owner, name, value, and hash.
- `xfs_parent_iread_extents` verifies that the attr fork exists and reads attr fork extents before parent operations.
- `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename` wrap logged attr set/remove/replace operations for directory changes.
- `xfs_parent_from_attr` validates and extracts parent inode/generation from a raw parent xattr.
- `xfs_parent_lookup` looks up a specific parent pointer while caller holds ILOCK.
- `xfs_parent_set` and `xfs_parent_unset` perform immediate non-transaction repair-oriented create/remove operations after sanity checking.

## Data and Invariants
- Parent pointer values are always local xattr values because `xfs_parent_rec` is only 12 bytes.
- Parent pointer updates always use logged operations; incomplete parent attrs are invalid.
- Parent-pointer-enabled files must have an attr fork, which inode creation pre-creates for linkable files.
- Parent pointer attr owner is generally the child inode.
- The parent generation is included in the value so stale parent inode reuse can be detected.

## Error Handling and Corruption Response
- Missing attr fork on a parent-pointer filesystem marks the inode parent metadata sick and returns `-EFSCORRUPTED`.
- Invalid raw parent attrs return `-EFSCORRUPTED`.
- Repair set/unset helpers assert and reject invalid name/value pairs before changing xattrs.

## Dependencies
This file depends on attr set/remove/replace/get machinery, DA attr geometry, directory name validation and hashing, transaction/deferred attr logging, inode fork extent loading, and parent pointer feature checks.

## Research Notes
Parent pointers deliberately reuse the xattr/DA infrastructure but impose stricter invariants: logged-only operations, local fixed-size values, directory-name-compatible names, and hashes mixed with parent inode numbers.
