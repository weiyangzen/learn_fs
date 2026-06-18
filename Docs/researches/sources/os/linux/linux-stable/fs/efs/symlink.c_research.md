# File Research: sources/os/linux/linux-stable/fs/efs/symlink.c

## Summary
Implements EFS symlink folio reads.

## Main Responsibilities
- Reads symlink target data from one or two EFS blocks.
- Rejects symlinks larger than two EFS blocks.
- Null-terminates the target in the folio.

## Key APIs
- `efs_symlink_aops`

## Important Behavior
The symlink read path maps block 0 and optionally block 1 through `efs_bmap()`, copies target bytes, appends `'\0'`, and completes the folio read.

## Risks
Symlink targets are limited to 1024 bytes. Failed block reads complete the folio with error.
