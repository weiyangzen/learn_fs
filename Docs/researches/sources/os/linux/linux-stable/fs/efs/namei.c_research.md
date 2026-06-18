# File Research: sources/os/linux/linux-stable/fs/efs/namei.c

## Summary
Implements EFS name lookup and NFS export filehandle helpers.

## Main Responsibilities
- Finds directory entries by linear scanning.
- Looks up child inodes by inode number.
- Converts export filehandles to dentries/parents.
- Finds a directory parent using the `..` entry.

## Key APIs
- `efs_lookup()`
- `efs_fh_to_dentry()`
- `efs_fh_to_parent()`
- `efs_get_parent()`

## Important Behavior
`efs_find_entry()` reads each mapped directory block, checks magic, walks slots, and compares names by length and bytes.

## Risks
Lookup is linear and block-format dependent. Directory corruption returns lookup miss or errors depending on where the failure occurs.
