# File Research: sources/os/linux/linux-stable/fs/qnx6/qnx6.h

## Summary
Private header for the QNX6 filesystem implementation.

## Main Responsibilities
- Define filesystem-endian integer typedefs.
- Define QNX6 superblock and inode wrapper structures.
- Provide endian conversion helpers controlled by mounted filesystem byte order.
- Provide mount option helpers.
- Declare inode, lookup, directory, MMI superblock, and directory-search interfaces.

## Key Interfaces
- `QNX6_SB()` and `QNX6_I()` access private superblock/inode data.
- `fs16_to_cpu()`, `fs32_to_cpu()`, and `fs64_to_cpu()` decode on-disk fields.
- `qnx6_mmi_fill_super()` is declared for MMI mounts.
- `qnx6_find_ino()` is declared for lookup.

## Cross-File Interactions
Included by all QNX6 implementation files and backed by UAPI QNX6 on-disk structures.
