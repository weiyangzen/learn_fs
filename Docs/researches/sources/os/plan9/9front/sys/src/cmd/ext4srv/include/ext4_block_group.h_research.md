# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_block_group.h

Inline accessor header for ext4 block group descriptors plus CRC16 declaration.

Key behavior:
- Gets/sets block bitmap, inode bitmap, and inode table first-block addresses with high 32-bit fields when descriptor size permits.
- Gets/sets free block count, free inode count, used directory count, and unused inode table count using high halves for 64-byte descriptors.
- Sets descriptor checksum and manages block group flags.
- Declares `ext4_bg_crc16`.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_super.h`.
- Used by allocation, mkfs, filesystem initialization, and checksum code.

Research notes:
- High address/count fields are used only when descriptor size is greater than the 32-byte minimum.
- `ext4_bg_has_flag` reads the on-disk flag word through `to_le16`.
