# File Research: sources/os/linux/linux-stable/fs/efs/dir.c

## Summary
Implements EFS directory file operations and readdir.

## Main Responsibilities
- Reads directory blocks through `sb_bread()`.
- Validates directory block magic.
- Iterates directory slots and emits entries.
- Checks entry bounds within a directory block.

## Key APIs
- `efs_dir_operations`
- `efs_dir_inode_operations`

## Important Behavior
Directory position encodes block and slot. Each block is mapped through `efs_bmap()`, checked for `EFS_DIRBLK_MAGIC`, then slots are walked and names emitted with `DT_UNKNOWN`.

## Risks
The code trusts many old on-disk layout fields after minimal checks. It does validate that name data remains inside the directory block before `dir_emit()`.
