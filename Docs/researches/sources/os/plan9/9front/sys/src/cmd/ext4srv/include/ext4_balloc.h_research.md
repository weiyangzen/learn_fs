# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_balloc.h

Public declarations for ext4 block allocation.

Key behavior:
- Declares block-to-group and group-to-starting-block conversion helpers.
- Declares block bitmap checksum setter.
- Declares single-block and range freeing from an inode.
- Declares goal-based block allocation and try-allocate-at-specific-block.

Notable dependencies:
- Includes `ext4_config.h`, `ext4_types.h`, and `ext4_fs.h`.
- Implemented by `ext4_balloc.c` and used by filesystem block mapping/truncation code.

Research notes:
- The API operates on `ext4_inode_ref` for allocation/freeing so inode block counts and dirty state can be updated with allocation metadata.
