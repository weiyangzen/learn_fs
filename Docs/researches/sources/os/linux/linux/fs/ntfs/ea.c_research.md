# File Research: sources/os/linux/linux/fs/ntfs/ea.c

## Purpose
Implements NTFS extended attribute handling, Linux xattr exposure, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage on top of NTFS `AT_EA` and `AT_EA_INFORMATION`.

## Key Elements
`ntfs_get_ea()` and `ntfs_set_ea()` read, replace, create, append, or remove EA entries while keeping `EA_INFORMATION` query length, packed length, and needed-EA count coherent. `ntfs_ea_lookup()` walks the packed EA list with size and alignment checks, and `ntfs_write_ea()` writes through an attribute inode using `ntfs_inode_attr_pwrite()`, optionally truncating old trailing data.

WSL metadata support maps `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` to Linux uid, gid, mode, and device number through `ntfs_ea_get_wsl_inode()` and `ntfs_ea_set_wsl_inode()`. Generic xattr listing enumerates EA names from `AT_EA`, while `ntfs_getxattr()` and `ntfs_setxattr()` special-case `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be` before falling back to EA storage.

`ntfs_new_attr_flags()` reconciles NTFS file attribute bits with resident/non-resident attribute record flags for sparse and compressed regular files. With POSIX ACL support, ACLs are serialized to xattrs, cached in the inode, and mode changes are mirrored back to `$LXMOD`.

## Dependencies And Integration
Uses Linux xattr and POSIX ACL APIs plus NTFS layout, attribute, index, directory, and EA headers. It relies on `ntfs_attr_readall()`, `ntfs_attr_add/remove/exist()`, `ntfs_attr_truncate()`, MFT record mapping, and attribute record resizing/mapping-pair update helpers.

## Behavior/Risks
EA mutation has partial rollback limits: `EA_INFORMATION` may be updated before `AT_EA`, so errors are surfaced and MFT records are dirtied carefully. Name length is capped at 255 bytes. Sparse/compressed flag changes are rejected for non-empty non-resident files and for invalid sparse+compressed combinations. Most public entry points reject operations after forced volume shutdown.
