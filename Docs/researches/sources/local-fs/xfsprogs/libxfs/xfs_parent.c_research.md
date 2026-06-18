# File Research: sources/local-fs/xfsprogs/libxfs/xfs_parent.c

## Role

This file implements parent pointer xattr handling. Parent pointers record directory parent identity in a child inode's attribute fork so metadata can reconstruct or validate directory relationships.

## Validation And Hashing

`xfs_parent_namecheck` validates parent pointer attr names. It rejects incomplete attrs and reuses directory name rules, so names cannot contain invalid dirent bytes.

`xfs_parent_valuecheck` requires the parent feature, a non-null local value exactly the size of `struct xfs_parent_rec`, and a valid parent directory inode number.

`xfs_parent_hashval` hashes the name using directory name hashing and mixes in the parent inode number to reduce hardlink collisions. `xfs_parent_hashattr` computes the hash from an xattr value after validating shape.

## DA Args Setup

`xfs_parent_da_args_init` initializes attr/da args for parent pointer operations:

- attr fork
- parent attr filter
- logged operations
- OKNOENT
- child inode as `dp`
- owner inode
- name/value from dirent name and parent record
- attr hash set by `xfs_attr_sethash`

`xfs_parent_iread_extents` ensures the child has an attr fork and loads attr extents before parent pointer updates, marking parent metadata sick on missing attr fork.

## Transactional Updates

- `xfs_parent_addname` adds a parent pointer after a dirent addition.
- `xfs_parent_removename` removes a parent pointer after a dirent removal.
- `xfs_parent_replacename` replaces an old parent/name record with a new one during rename.

Each builds `xfs_parent_rec` from the parent directory inode generation and inode number and delegates to logged attr set/remove/replace helpers.

## Parsing And Repair Helpers

`xfs_parent_from_attr` extracts parent inode and generation from a parent xattr, returning zero for valid parent pointers and `-EFSCORRUPTED` for malformed data.

`xfs_parent_lookup` looks up a specific parent pointer under an already locked inode.

`xfs_parent_set` and `xfs_parent_unset` are immediate non-transaction repair helpers that sanity-check the name/value, initialize scratch da args, and call `xfs_attr_set` with create or remove mode.

## Dependencies

This file depends on attr fork operations, directory name validation/hash, inode generation, transaction/defer infrastructure, health marking, bmap extent loading, and parent feature predicates.

## Research Notes

Parent pointer values are deliberately small enough to stay local, avoiding remote attr value handling. Missing attr forks are treated as corruption because parent-enabled filesystems create attr forks for linkable inodes at creation time.
