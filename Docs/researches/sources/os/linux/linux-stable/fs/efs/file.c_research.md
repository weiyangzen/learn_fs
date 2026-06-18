# File Research: sources/os/linux/linux-stable/fs/efs/file.c

## Summary
Provides EFS block mapping helpers for regular file reads.

## Main Responsibilities
- Maps logical file blocks to physical blocks.
- Rejects create/write block mapping requests.
- Bounds block access by `inode->i_blocks`.

## Key APIs
- `efs_get_block()`
- `efs_bmap()`

## Important Behavior
`efs_get_block()` returns `-EROFS` for create requests and maps existing blocks through `efs_map_block()`. `efs_bmap()` validates negative and past-EOF block numbers before mapping.

## Risks
All I/O depends on correctness of `efs_map_block()` from `inode.c`; this file mainly enforces read-only behavior and range checks.
